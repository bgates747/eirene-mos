"""Validate returned Console8 startup/UART evidence without writing its card."""
from pathlib import Path
import hashlib,importlib.util,json,re,statistics,sys
root=Path(__file__).resolve().parents[2];archive=Path(sys.argv[1]);build=Path(sys.argv[2]);card=archive/'returned'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((archive/'receipt.json').read_text());deploy=json.loads((root/'docs/tasks/IRQ-001/deployment.json').read_text());info=json.loads((build/'build-info.json').read_text())
assert receipt['card_unchanged'] and not receipt['card_writes'] and not receipt['physical_operations']
assert receipt['volume']['label']=='AGONC8' and receipt['volume']['uuid']=='8658-1C23'
assert h(archive/'returned.tar.gz')==receipt['archive_sha256']
assert {str(p.relative_to(card)) for p in card.rglob('*') if p.is_file()}==set(receipt['files'])
for n,d in receipt['files'].items():assert h(card/n)==d['sha256'],n
mutable={'before/next.txt','after/next.txt'}
for n,d in deploy['card_files'].items():
 if n not in mutable:assert h(card/n)==d['sha256'],('Deployed input changed',n)
assert h(card/'mos-before.bin')==info['baseline_sha256'] and h(card/'mos-fixed.bin')==info['fixed_sha256']
for name,app in (('functional','test.bin'),('example','example.bin'),('perf','perf.bin')):assert h(card/'after'/app)==info['applications'][name]['sha256']
assert h(card/'before/irqcheck.bin')==h(card/'after/irqcheck.bin')==info['probe_sha256']
identity=(build/'probe/src/identity.h').read_text();expected=[int(x,16) for x in re.search(r'expected\[48\]=\{(.*?)\}',identity)[1].split(',')]
default=int(re.search(r'#define DEFAULT_IRQ (\d+)',identity)[1]);assert len(expected)==48
seeds=deploy['report_seeds'];validated=[]
for folder,fixed in (('before',False),('after',True)):
 start=seeds[folder];assert sorted(p.name for p in (card/folder).glob('I*.log'))==[f'I{n:04}.log' for n in (start,start+1)]
 for offset,phase,hard in ((0,'cold',1),(1,'warm-poisoned',0)):
  p=card/folder/f'I{start+offset:04}.log';text=p.read_text();lines=text.splitlines();crc=info['fixed_crc32' if fixed else 'baseline_crc32'];case='fixed' if fixed else 'original'
  assert lines[0]==f'IRQ build={info["probe_build"]} case={case} phase={phase} CRC32={crc} hardReset={hard}'
  slots=re.findall(r'^SLOT ([0-9A-F]{2}) opcode=([0-9A-F]{2}) target=([0-9A-F]{6}) expected=([0-9A-F]{6}) (OK|BAD)$',text,re.M)
  assert len(slots)==48 and [int(s[0],16) for s in slots]==list(range(0,96,2))
  for i,(vector,op,target,want,status) in enumerate(slots):
   assert int(want,16)==expected[i],(p,i,'expected target')
   good=fixed or expected[i]!=default
   assert (int(op,16),int(target,16),status)==((0xc3,expected[i],'OK') if good else (0,0,'BAD')),(p,i)
  summary='SUMMARY slots=48 bad=0 zero=0 active_bad=0 UART1_admission=ACCEPT' if fixed else 'SUMMARY slots=48 bad=45 zero=45 active_bad=0 UART1_admission=REFUSE'
  assert lines.count(summary)==1 and lines[-1]==('IRQ FIX PASS' if fixed else 'IRQ ORIGINAL REPRODUCED')
  if fixed:assert lines.count('VECTOR ROUNDTRIPS 48/48')==1
  assert 'IRQ UNEXPECTED FAIL' not in text
  validated.append(dict(file=str(p.relative_to(card)),kind='startup',phase=phase,hardReset=hard,ROM_crc32=crc,slots=48,default_slots_zero=0 if fixed else 45,vector_roundtrips=48 if fixed else 0,expected_outcome_verified=True,sha256=h(p)))
 assert (card/folder/'phase.txt').read_text()=='0'
 assert int((card/folder/'next.txt').read_text())==start+(5 if fixed else 2)
assert not list((card/'before').glob('R*.log'))
start=seeds['after']+2;assert sorted(p.name for p in (card/'after').glob('R*.log'))==[f'R{n:04}.log' for n in range(start,start+3)]
journal=(card/'after/runs.log').read_text().splitlines();want_journal=[]
markers=('MODE async','Ordinary RST18 before opt-in PASS','Comparator negative/positive PASS','Zero-length refusal; context is a caller precondition PASS','Boundary lengths1/15/16/17/255/256/257/1024 and NULL callback PASS','Single source/BUSY/callback/input-hook/RX-during-TX PASS','VERIFY8192 PASS','Ordinary RST18 after finish PASS','TM001 MINIMAL PASS','RC2 PASS')
for n in (start,start+1):
 p=card/'after'/f'R{n:04}.log';text=p.read_text();lines=text.splitlines()
 assert lines[0]=='TM001 build='+info['probe_build'] and 'FAIL' not in text
 assert lines.count(f'RC2 MOS bytes={info["bytes"]} CRC32={info["fixed_crc32"]} expected={info["fixed_crc32"]}')==1
 for marker in markers:assert lines.count(marker)==1,(p,marker)
 assert lines.count('Receiver verification quarter complete')==4
 for state in ('START','PASS'):want_journal.append(f'R{n:04} {state} RC2 build={info["probe_build"]}')
 validated.append(dict(file=str(p.relative_to(card)),kind='UART functional',receiver_bytes=8192,passed=True,sha256=h(p)))
spec=importlib.util.spec_from_file_location('metrics',root/'experiments/uart0-performance2/metrics.py');metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
p=card/'after'/f'R{start+2:04}.log';perf=metrics.read_report(p.read_text());cfg=(build/'perf/src/zz_config.c').read_text()
assert perf['case']=='irq-startup-fix' and perf['build'] in cfg and perf['config']['transport']==1
assert perf['mos_bytes']==info['bytes'] and perf['mos_crc32']==int(info['fixed_crc32'],16)
assert all(t['missed']==0 for t in perf['trials'])
for state in ('START','PASS'):want_journal.append(f'R{start+2:04} {state} PERF2 build={perf["build"]} case={perf["case"]}')
assert journal==want_journal
validated.append(dict(file=str(p.relative_to(card)),kind='PERF2',receiver_bytes=9*8192,trials=9,passed=True,sha256=h(p)))
summary={}
for scenario,name in ((0,'bulk-only'),(1,'paced-plus-work'),(2,'bulk-plus-work')):
 rows=[t for t in perf['trials'] if t['scenario']==scenario];remaining=100*statistics.median(t['foreground_capacity_fraction'] for t in rows)
 summary[name]=dict(payload_Bps=statistics.median(t['payload_Bps'] for t in rows),work_steps_per_second=statistics.median(t['work_per_second'] for t in rows) if scenario else None,foreground_compute_remaining_percent=remaining if scenario else None,sending_cost_percent=100-remaining if scenario else None,work_measurement='enabled' if scenario else 'disabled by scenario design',missed=sum(t['missed'] for t in rows))
# Earlier matched run is context, not a newly repeated original/fixed A/B.
prior=metrics.read_report((root/'docs/tasks/TR-001/hardware/R0059.log').read_text());comparison={}
for scenario,name in ((0,'bulk-only'),(1,'paced-plus-work'),(2,'bulk-plus-work')):
 a=[t for t in prior['trials'] if t['scenario']==scenario];b=[t for t in perf['trials'] if t['scenario']==scenario]
 comparison[name]=dict(payload_rate_change_percent=100*(statistics.median(t['payload_Bps'] for t in b)/statistics.median(t['payload_Bps'] for t in a)-1),work_rate_change_percent=(100*(statistics.median(t['work_per_second'] for t in b)/statistics.median(t['work_per_second'] for t in a)-1)) if scenario else None)
allowed=set(deploy['card_files'])|{r['file'] for r in validated}|{'before/phase.txt','after/phase.txt','after/runs.log'}
assert set(receipt['files'])==allowed,('Unexpected files',set(receipt['files'])^allowed)
result=dict(passed=True,physical=True,board='Heber Agon Console8',firmware_source=info['source_commit'],baseline_source=info['baseline_source'],reports=validated,slot_observations=192,fixed_install_restore_pairs=96,verified_payload_bytes=90112,performance_trials=9,missed_deadlines=0,summary=summary,parsed_PERF2=perf,previous_TRIM_context=comparison,report_counters={'before':62,'after':67},all_deployed_firmware_apps_unchanged=True,VDP=dict(name='Stock Bistromathics 2.16.0',basis='Prescribed protocol and Author report that tests are complete',independently_fingerprinted=False),example=dict(basis='Author overall completion report; app writes no report',independently_logged=False),archive_sha256=receipt['archive_sha256'],card_modified=False,upstream_notified=False,release_promoted=False,limitations=['The previous TRIM benchmark was an earlier session, not a newly matched speed comparison.','Foreground capacity is a calculation-overlap proxy, not direct exclusive CPU profiling.','Default-table reads and setintvector roundtrips are not peripheral IRQ stress.','No hardware wire capture or independent VDP identity/example transcript was recorded.'])
(archive/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,reports=len(validated),verified_payload_bytes=90112,summary=summary,previous_TRIM_context=comparison)))
