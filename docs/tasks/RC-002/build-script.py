from pathlib import Path
import hashlib,io,json,os,re,shutil,subprocess,tarfile,zlib,zipfile
r=Path('/home/smith/Agon/mystuff/eirene-mos-rc1');b=r/'build/tm001';out=b/'rc2-001';out.mkdir(exist_ok=False);tool=Path('/home/smith/Agon/mystuff/agon-mos/build/uart0-suite/toolchain/agondev');old=b/'tr001-002';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not subprocess.check_output(['git','status','--porcelain'],cwd=r).strip();commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();raw=subprocess.check_output(['git','archive',commit],cwd=r)
def make(p,name):
 with (out/(name+'.log')).open('w') as f:subprocess.run(['make','AGONDEV_TOOLCHAIN='+str(tool)],cwd=p,stdout=f,stderr=subprocess.STDOUT,check=True)
for name in ('firmware','repeat'):
 p=out/name;p.mkdir()
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(p,filter='data')
 make(p,name)
f=out/'firmware';rom=f/'bin/mos.bin';assert h(rom)==h(out/'repeat/bin/mos.bin')
changed=[]
for p in (f/'src').rglob('*'):
 if p.is_file() and h(p)!=h(old/'trim/src'/p.relative_to(f/'src')):changed.append(str(p.relative_to(f/'src')))
assert changed==['version.h'],changed
objects=[]
for p in (f/'obj').glob('*.o'):
 if h(p)!=h(old/'trim/obj'/p.name):objects.append(p.name)
assert objects==['main.o'],objects
assert b'Eirene UART0\x00' in rom.read_bytes() and b'RC \x00' in rom.read_bytes()
crc=zlib.crc32(rom.read_bytes());apps={}
def copyapp(src,dst):
 shutil.copytree(src,dst,ignore=shutil.ignore_patterns('obj','bin','__pycache__'));return dst
for name in ('functional','example'):
 p=copyapp(old/name,out/name)
 if name=='example':
  shutil.rmtree(p/'src');shutil.copytree(r/'examples/uart0-async/src',p/'src');shutil.copyfile(r/'experiments/uart0-release/src/rom_crc.h',p/'src/rom_crc.h')
 else:
  a=p/'src/main.c';a.write_text(a.read_text().replace('TRIM1','RC2'))
 (p/'src/identity.h').unlink(missing_ok=True)
 pins={str(x.relative_to(p)):h(x) for x in sorted(p.rglob('*')) if x.is_file()};ident=hashlib.sha256(json.dumps(dict(source=pins,MOS=h(rom)),sort_keys=True).encode()).hexdigest()[:16]
 (p/'src/identity.h').write_text(f'#define TM_BUILD "{ident}"\n#define RC_MOS_BYTES {rom.stat().st_size}\n#define RC_MOS_CRC {hex(crc)}UL\n');make(p,name)
 binary=p/'bin'/('test.bin' if name=='functional' else 'example.bin');apps[name]=dict(build=ident,sha256=h(binary),source_sha256={str(x.relative_to(p)):h(x) for x in sorted((p/'src').rglob('*')) if x.is_file()})
registry=json.loads((old/'perf/cases.json').read_text());cases=[]
for c in registry['cases']:
 command='rc2' if c['command']=='trim' else c['command'];p=copyapp(old/'perf'/c['command']/'fixture',out/'perf'/command)
 if command=='rc2':
  mk=p/'Makefile';mk.write_text(mk.read_text().replace('NAME = trim','NAME = rc2'));c.update(command='rc2',case='uart0-rc2',name='Eirene UART0 RC2',mos_bytes=rom.stat().st_size,mos_crc=crc,MOS_sha256=h(rom),map_sha256=h(f/'bin/mos.map'),firmware='mos-rc2.bin',app='rc2.bin')
  c['build']=hashlib.sha256(json.dumps(dict(commit=commit,case=c['case'],MOS=h(rom)),sort_keys=True).encode()).hexdigest()[:16]
  (p/'src/zz_config.c').write_text('#include "config.h"\nconst struct FixtureConfig fixture={'+','.join(json.dumps(v) for v in (c['case'],command,c['name'],c['build']))+',1,'+str(c['mos_bytes'])+','+hex(crc)+'UL};\n')
 make(p,command+'-perf');assert h(p/'obj/main.o')==h(old/'perf/stock/fixture/obj/main.o');assert h(p/'obj/platform.o')==h(old/'perf/stock/fixture/obj/platform.o')
 if command!='rc2':assert h(p/'bin'/c['app'])==c['app_sha256']
 c.update(app_sha256=h(p/'bin'/c['app']),source=command+'-source.json');cases.append(c)
info=dict(tag='3.1.0_uart0_rc_2',source_commit=commit,upstream_commit='86b694260e3be3b391284ce4aa8ecc758f7f34e9',MOS_bytes=rom.stat().st_size,MOS_crc32=f'{crc:08X}',MOS_sha256=h(rom),map_sha256=h(f/'bin/mos.map'),clean_rebuild_identical=True,changes_from_hardware_tested_image=changed,changed_objects=objects,sender_object_identical=True,sender_text_bytes=286,sender_BSS_bytes=9,applications=apps,toolchain=json.loads((old/'build-info.json').read_text())['toolchain'],exact_RC2_branding_hardware_tested=False,hardware_tested_implementation=dict(source_commit='df2066832ecb6a6a33a817acb8b9f41d609e44cc',MOS_sha256=h(old/'trim/bin/mos.bin'),reports=['R0054','R0055','R0056','R0057','R0058','R0059']))
(out/'build-info.json').write_text(json.dumps(info,indent=2)+'\n');(out/'cases.json').write_text(json.dumps(dict(schema='PERF2-RC2',reference='official-stock',cases=cases),indent=2)+'\n')
pkg=out/info['tag'];pkg.mkdir()
def sourcecopy(src,dst):shutil.copytree(src,dst,ignore=shutil.ignore_patterns('bin','obj','build','__pycache__'))
sourcecopy(f,pkg/'source');sourcecopy(out/'functional',pkg/'fixture');sourcecopy(out/'example',pkg/'example')
for name in ('stock','rc1','rc2'):sourcecopy(out/'perf'/name,pkg/'benchmarks'/name)
for src,dst in ((rom,'mos-rc2.bin'),(f/'bin/mos.map','mos-rc2.map'),(out/'functional/bin/test.bin','test.bin'),(out/'example/bin/example.bin','example.bin'),(out/'functional/checks.bin','checks.bin'),(b/'rc1-003/firmware/bin/mos.bin','mos-rc1.bin'),(b/'tr001-package001/appliance/mos-stock.bin','mos-stock.bin'),(out/'build-info.json','build-info.json'),(out/'cases.json','cases.json')):shutil.copyfile(src,pkg/dst)
for c in cases:
 shutil.copyfile(out/'perf'/c['command']/'bin'/c['app'],pkg/c['app']);(pkg/c['source']).write_text(json.dumps(c,indent=2)+'\n')
shutil.copytree(b/'tr001-package001/appliance/licenses',pkg/'licenses');shutil.copytree(r/'docs/tasks/TR-001/hardware',pkg/'evidence/console8');shutil.copyfile(r/'docs/tasks/TR-001/hardware.json',pkg/'evidence/hardware-analysis.json');shutil.copyfile(r/'docs/tasks/TR-001/hardware-results.md',pkg/'evidence/hardware-results.md')
(out/'summary.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps({k:info[k] for k in ('source_commit','MOS_bytes','MOS_crc32','MOS_sha256','changes_from_hardware_tested_image','changed_objects')}))
