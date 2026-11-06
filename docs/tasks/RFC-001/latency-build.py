from pathlib import Path
import hashlib,json,os,signal,subprocess,sys,time
root=Path('/Agon/mystuff/eirene-mos');out=Path(sys.argv[2]);token=sys.argv[1];tool=root/'build/rc003/toolchain'
lease=['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/pi5-workloads/pi5_lease.py','assert-owner','--owner','agon-mos','--lease',token]
subprocess.run(lease,check=True)
cmd=['make','AGONDEV_TOOLCHAIN='+str(tool)];start=time.monotonic();proc=None
try:
 with (out/'build.log').open('w') as log:
  proc=subprocess.Popen(cmd,cwd=out/'fixture',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  while proc.poll() is None:
   temp=int(Path('/sys/class/thermal/thermal_zone0/temp').read_text());avail=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
   if time.monotonic()-start>180 or temp>=80000 or avail<524288:raise RuntimeError('finite/thermal/memory guard')
   time.sleep(.2)
  if proc.returncode:raise RuntimeError('build failed; retain logs before correction')
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 binary=out/'fixture/bin/test.bin'
 info=dict(passed=True,seconds=time.monotonic()-start,app_bytes=binary.stat().st_size,app_sha256=h(binary),source=json.loads((out/'source.json').read_text()),libagon=h(tool/'lib/libagon.a'))
 (out/'build.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))
finally:
 if proc and proc.poll() is None:os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=10)
