from pathlib import Path
import hashlib,importlib.util,io,json,os,re,shlex,shutil,signal,subprocess,sys,tarfile,time,zlib
ROOT=Path('/Agon/mystuff/eirene-mos');OUT=ROOT/'build/rc003/native-r02';OUT.mkdir(exist_ok=False)
TOOL=ROOT/'build/rc003/toolchain';TOKEN=sys.argv[1];START=time.monotonic()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def assertlease():subprocess.run(['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py','assert-owner','--owner','agon-mos','--lease',TOKEN],check=True,stdout=subprocess.DEVNULL)
def command(cmd,cwd,log,limit=120):
 assertlease();begin=time.monotonic()
 with log.open('w') as f:
  f.write(shlex.join(cmd)+'\n');f.flush();p=subprocess.Popen(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   while p.poll() is None:
    if time.monotonic()-begin>limit or time.monotonic()-START>900:raise TimeoutError(str(cmd))
    temp=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text())/1000
    avail=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
    if temp>=80 or avail<512*1024:raise RuntimeError(f'thermal/memory guard {temp}C {avail}KiB')
    time.sleep(.2)
   if p.returncode:raise RuntimeError(f'{cmd[0]} failed; see {log}')
  finally:
   if p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
 return time.monotonic()-begin
def snapshot(name,commit):
 p=OUT/name;p.mkdir();raw=subprocess.check_output(['git','-C',str(ROOT),'archive',commit])
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(p,filter='data')
 return p
def make(p,name):return command(['make','AGONDEV_TOOLCHAIN='+str(TOOL)],p,OUT/(name+'.log'))
def symbols(p,name):
 line=next(l for l in (OUT/(name+'.log')).read_text().splitlines() if '/ez80-none-elf-ld ' in l)
 cmd=shlex.split(line);cmd[cmd.index('--oformat')+1]='elf32-z80';cmd[cmd.index('-o')+1]=str(p/'bin/mos.elf');cmd=[('-Map='+str(p/'bin/mos.elf.map')) if a.startswith('-Map=') else a for a in cmd]
 command(cmd,p,OUT/(name+'-elf.log'))
 command([str(TOOL/'bin/ez80-none-elf-objcopy'),'-O','binary',str(p/'bin/mos.elf'),str(p/'bin/from-elf.bin')],p,OUT/(name+'-objcopy.log'))
 assert h(p/'bin/from-elf.bin')==h(p/'bin/mos.bin')
 text=subprocess.check_output([str(TOOL/'bin/ez80-none-elf-nm'),'-n',str(p/'bin/mos.elf')],text=True);s={}
 for line in text.splitlines():
  fields=line.split()
  if len(fields)>=3:
   try:s[fields[-1]]=int(fields[0],16)
   except ValueError:pass
 (p/'bin/symbols.json').write_text(json.dumps(s,indent=2)+'\n');return s
spec=importlib.util.spec_from_file_location('startup',ROOT/'experiments/irq-startup/verify.py');startup=importlib.util.module_from_spec(spec);spec.loader.exec_module(startup)
commits={'rc1-old':'47dd56129c0043931bb32f7d329c0392a0b8a809','rc1':'d268d0b344dde678250ef692986c7d8bf79f7c4b','rc2-old':'825eaf77176247f5b5ba2f940ae73fcace34e7e5','rc2':'b219486068b41af8a760f7e4c6b132eea43377b1','rc3':subprocess.check_output(['git','-C',str(ROOT/'build/rc003/rc3-source'),'rev-parse','HEAD'],text=True).strip()}
rows={};paths={}
for name,commit in commits.items():
 p=snapshot(name,commit);paths[name]=p;duration=make(p,name);s=symbols(p,name);rom=p/'bin/mos.bin';data=rom.read_bytes()
 try:proof=startup.verify(data,s);fixed=True
 except AssertionError as e:proof={'rejected':str(e)};fixed=False
 assert fixed==(not name.endswith('-old')),(name,proof)
 rows[name]=dict(commit=commit,bytes=len(data),sha256=h(rom),crc32=f'{zlib.crc32(data):08X}',map_sha256=h(p/'bin/mos.map'),startup=proof,build_seconds=duration)
 expected={'rc1-old':'49873fb817f47cc76f50b8cec1c3d9cde7b252ac2ec844e08e745bdaf1c5eeab','rc2-old':'a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a','rc2':'4550f60e74bb7be7d99e4fd1acaddaf9ac43d5b02a242fadee60c6e92aec30dc'}
 if name in expected:assert rows[name]['sha256']==expected[name],(name,rows[name]['sha256'])
 print(json.dumps({'built':name,**rows[name]}),flush=True)
 if name in ['rc1','rc2']:
  old=paths[name+'-old'];changed=[str(f.relative_to(p/'src')) for f in (p/'src').rglob('*') if f.is_file() and h(f)!=h(old/'src'/f.relative_to(p/'src'))]
  objects=[f.name for f in (p/'obj').glob('*.o') if h(f)!=h(old/'obj'/f.name)]
  assert changed==['init.asm'] and objects==['init.o'],(changed,objects)
  assert (p/'bin/mos.bin').stat().st_size==(old/'bin/mos.bin').stat().st_size
  rows[name].update(changed_sources=changed,changed_objects=objects,sender_unchanged=True)
# Independent fresh RC3 build must be byte-identical.
p=snapshot('rc3-repeat',commits['rc3']);make(p,'rc3-repeat');assert h(p/'bin/mos.bin')==rows['rc3']['sha256'];rows['rc3']['clean_rebuild_identical']=True
apps={}
for name in ['rc1','rc2']:
 base=ROOT/'build/tm001'/('rc1-003' if name=='rc1' else 'irq001-build001');apps[name]={}
 for kind,source in [('functional',base/('fixture' if name=='rc1' else 'functional')),('example',base/'example')]:
  dst=OUT/'apps'/name/kind;shutil.copytree(source,dst,ignore=shutil.ignore_patterns('obj','bin','__pycache__'))
  (dst/'src/identity.h').unlink(missing_ok=True)
  pins={str(f.relative_to(dst)):h(f) for f in sorted((dst/'src').rglob('*')) if f.is_file()};build=hashlib.sha256(json.dumps(dict(source=pins,mos=rows[name]['sha256']),sort_keys=True).encode()).hexdigest()[:16]
  (dst/'src/identity.h').write_text(f'#define TM_BUILD "{build}"\n#define RC_MOS_BYTES {rows[name]["bytes"]}\n#define RC_MOS_CRC 0x{rows[name]["crc32"]}UL\n')
  make(dst,name+'-'+kind);binary=dst/'bin'/('test.bin' if kind=='functional' else 'example.bin')
  apps[name][kind]=dict(build=build,path=str(dst),binary_sha256=h(binary),source_sha256={str(f.relative_to(dst)):h(f) for f in sorted((dst/'src').rglob('*')) if f.is_file()})
# RC3 fixture generated from its own frozen source/map; recipe has no ROM allowlist.
p=paths['rc3'];spec=importlib.util.spec_from_file_location('prepare',p/'experiments/uart0-rfc/prepare.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
f=m.prepare(OUT/'apps/rc3',p/'bin/mos.bin',p/'bin/mos.map');dst=OUT/'apps/rc3/fixture';make(dst,'rc3-functional')
example=OUT/'apps/rc3/example';shutil.copytree(p/'examples/uart0-async',example);make(example,'rc3-example')
apps['rc3']={'functional':dict(path=str(dst),binary_sha256=h(dst/'bin/test.bin'),generated=f),'example':dict(path=str(example),binary_sha256=h(example/'bin/example.bin'))}
# Publish a proven foreign-ROM refusal control only in the model campaign.
info=dict(schema='RC003-build-1',candidates=rows,apps=apps,toolchain={n:h(TOOL/'bin'/n) for n in ['ez80-none-elf-clang','ez80-none-elf-as','ez80-none-elf-ld']},libagon_sha256=h(TOOL/'lib/libagon.a'),elapsed_seconds=time.monotonic()-START)
(OUT/'build-info.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps({'complete':True,'candidates':rows,'elapsed_seconds':info['elapsed_seconds']},indent=2),flush=True)
