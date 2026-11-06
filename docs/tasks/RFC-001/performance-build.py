from pathlib import Path
import hashlib,json,os,re,signal,subprocess,sys,time
r=Path('/Agon/mystuff/eirene-mos');out=Path(sys.argv[2]);token=sys.argv[1];tool=r/'build/rc003/toolchain';start=time.monotonic();rows=[]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
lease=['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py','assert-owner','--owner','agon-mos','--lease',token]
def command(argv,cwd,log):
 subprocess.run(lease,check=True,stdout=subprocess.DEVNULL)
 p=None;t=time.monotonic()
 try:
  with log.open('w') as f:
   p=subprocess.Popen(argv,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   while p.poll() is None:
    temp=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text());avail=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
    if time.monotonic()-t>180 or time.monotonic()-start>600 or temp>=80000 or avail<524288:raise RuntimeError('time/thermal/memory stop')
    time.sleep(.2)
   if p.returncode:raise RuntimeError('compile/check failed; retain '+str(log))
 finally:
  if p and p.poll() is None:os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=10)
for name in ['smoke','full']:
 app=out/name;command(['make','AGONDEV_TOOLCHAIN='+str(tool)],app,out/(name+'-build.log'))
 binary=app/'bin'/('smoke.bin' if name=='smoke' else 'test.bin');mapfile=binary.with_suffix('.map')
 text=mapfile.read_text();bss=int(re.search(r'0x([0-9a-f]+)\s+bss_end\s*=',text).group(1),16);assert bss<0xb0000
 command([str(tool/'bin/ez80-none-elf-objdump'),'-d',str(app/'obj/api.o')],app,out/(name+'-bridge-disassembly.txt'))
 rows.append(dict(kind=name,bytes=binary.stat().st_size,sha256=h(binary),map_sha256=h(mapfile),bss_end=hex(bss),source={str(f.relative_to(app)):h(f) for f in sorted((app/'src').rglob('*')) if f.is_file()}))
 print(json.dumps(rows[-1]),flush=True)
info=dict(compiled=True,target_executed=False,hardware=False,seconds=time.monotonic()-start,mos_sha256='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50',libagon_sha256=h(tool/'lib/libagon.a'),cases=rows)
(out/'build.json').write_text(json.dumps(info,indent=2)+'\n')
