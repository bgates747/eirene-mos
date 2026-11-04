"""Finite Oryx leased functional campaign. First failure stops the campaign."""
from pathlib import Path
import json,os,shlex,shutil,signal,subprocess,sys,time
root=Path(__file__).resolve().parents[2];out=root/'build/tm001'/sys.argv[1]
profiles=json.loads((out/'profiles.json').read_text());results=[]
def lease():
 token=os.environ['UART0_ORYX_LEASE'];env=root.parent/'agon-dev-env'
 args=[str(env/'.venv/bin/python'),str(env/'cross-agent/vdplet-rollout/oryx_lease.py'),'assert-owner','--owner','agon-mos','--lease',token]
 subprocess.run(['ssh','-o','BatchMode=yes','raspberrypi',shlex.join(args)],check=True,stdout=subprocess.DEVNULL)
for row in profiles['profiles']:
 p=Path(row['path']);r=p/'results';r.mkdir();art=p/'last-run';proc=None;error=None;start=time.monotonic()
 try:
  for pin in ('.runtime.sha256','.mos-release.sha256'):subprocess.run(['sha256sum','--check','--status',pin],cwd=p,check=True)
  with (r/'frontend.log').open('w') as log:
   lease() # immediately before every actual emulator process
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=row['engine']),start_new_session=True)
   n=0;last=start
   while time.monotonic()-start<300:
    f=art/'mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
    if len(wire)!=n:n=len(wire);last=time.monotonic()
    if b'IRQ001 CLI RETURN' in wire:break
    assert b'TM001 MINIMAL FAIL' not in wire and b'PERF1 FAIL' not in wire and b'PERF2 FAIL' not in wire,'Fixture reports FAIL'
    assert b'Error executing autoexec' not in wire,'MOS command failed'
    assert b'IRQ UNEXPECTED FAIL' not in wire and b'IRQ UNKNOWN MOS' not in wire,'Unexpected startup result'
    assert b'Guru meditation' not in wire and b'RST $38 panic' not in wire,'Guest panic'
    assert proc.poll() is None,'Frontend exited early'
    assert time.monotonic()-last<45,'No UART progress for45seconds'
    time.sleep(.1)
   else:raise TimeoutError('300second cell limit')
 except Exception as exc:error=repr(exc)
 finally:
  if proc and proc.poll() is None:
   expected=(p/'flexe-agon-emulator.bin').resolve()
   for child in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(child.name))==proc.pid and (child/'exe').resolve()==expected:os.kill(int(child.name),signal.SIGTERM)
    except (OSError,PermissionError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  if art.exists():shutil.copytree(art,r/'raw')
  reports=r/'reports';reports.mkdir();subprocess.run(['mcopy','-s','-i',str(p/'card.img'),'::/irq/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
 try:
  assert error is None,error
  kind=row['kind'];wire=(r/'raw/mos-to-vdp.bin').read_bytes().decode('latin1')
  if kind.startswith('startup'):
   assert sorted(f.name for f in reports.glob('I*.log'))==['I0001.log','I0002.log']
   assert int((reports/'next.txt').read_text())==3
   fixed=kind=='startup-fixed'
   for number,phase,hard in ((1,'cold',1),(2,'warm-poisoned',0)):
    report=(reports/f'I{number:04}.log').read_text()
    assert f'phase={phase}' in report and f'hardReset={hard}' in report
    assert 'build='+row['probe_build'] in report and report.count('SLOT ')==48
    assert ('IRQ FIX PASS' if fixed else 'IRQ ORIGINAL REPRODUCED') in report
    assert ('bad=0 zero=0 active_bad=0 UART1_admission=ACCEPT' if fixed else 'bad=45 zero=45 active_bad=0 UART1_admission=REFUSE') in report
    assert report.count(' OK')==(48 if fixed else 3)
    if fixed:assert 'VECTOR ROUNDTRIPS 48/48' in report
   assert 'IRQ COLD/WARM PAIR COMPLETE' in wire and (reports/'phase.txt').read_text()=='0'
  elif kind=='uart':
   for number in (1,2):
    report=(reports/f'R{number:04}.log').read_text()
    for marker in ('RC2 PASS','VERIFY8192 PASS','RX-during-TX PASS','NULL callback PASS','Ordinary RST18 after finish PASS'):assert marker in report
   assert int((reports/'next.txt').read_text())==3 and 'RC2 EXAMPLE PASS' in wire
  else:
   import importlib.util
   spec=importlib.util.spec_from_file_location('metrics',root/'experiments/uart0-performance2/metrics.py');metrics=importlib.util.module_from_spec(spec);spec.loader.exec_module(metrics)
   report=(reports/'R0001.log').read_text();data=metrics.read_report(report)
   assert data['case']=='irq-startup-fix' and all(d['missed']==0 for d in data['trials'])
   assert int((reports/'next.txt').read_text())==2
  stats=json.loads((r/'raw/stats.json').read_text());uart=json.loads((r/'raw/uart.json').read_text())
  assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped'))
  assert uart['tx_drops']==uart['rx_overruns']==0
 except Exception as exc:
  if error is None:error=repr(exc)
 result=dict(**row,passed=error is None,error=error,elapsed=time.monotonic()-start,receiver_bytes=(16384 if row['kind']=='uart' else (73728 if row['kind']=='perf' else 0)) if error is None else 0)
 (r/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result);(out/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
 if error:raise SystemExit('Campaign stopped at first failed cell')
