"""Finite real-PS/2-input campaign; no target memory/timer/vector injection."""
from pathlib import Path
import importlib.util,json,os,re,signal,subprocess,sys,time
root=Path('/home/smith/Agon/mystuff/eirene-mos/.emulator/rfc001-lat001');inputs=root.parents[1]/'build/rfc001/lat001-inputs';rows=json.loads((root/'profiles.json').read_text());results=[];campaign=time.monotonic()
spec=importlib.util.spec_from_file_location('oracle',inputs/'check_wire.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle);print(oracle.selftest(),flush=True)
for row in rows:
 p=Path(row['path']);proc=None;error=None;control=None;start=time.monotonic();actions=[]
 try:
  for f in ['.runtime.sha256','.mos-release.sha256']:subprocess.run(['sha256sum','--check','--status',f],cwd=p,check=True)
  subprocess.run(['ssh','-o','BatchMode=yes','raspberrypi','/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/vdplet-rollout/oryx_lease.py','assert-owner','--owner','agon-mos','--lease',sys.argv[1]],check=True,stdout=subprocess.DEVNULL)
  fifo=p/'control.fifo';os.mkfifo(fifo);control=os.open(fifo,os.O_RDWR|os.O_NONBLOCK)
  env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=row['engine'],LD_PRELOAD=str(p/'capture_shim.so'),AMP_CAPTURE_DIR=str(p),AMP_CONTROL_FIFO=str(fifo))
  with (p/'frontend.log').open('w') as log:
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=env)
   old=0;last=start;finish=None;sent=set();pending=[]
   while time.monotonic()-start<300 and time.monotonic()-campaign<900:
    now=time.monotonic();f=p/'last-run/mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
    if len(wire)!=old:old=len(wire);last=now
    for m in re.finditer(rb'LAT BEGIN case=(\d+) mode=(\d) pause=(\d);',wire):
     case=int(m.group(1))
     if case not in sent:
      sent.add(case)
      for delay,down in [(.03,1),(.08,0),(.15,1),(.20,0)]:pending.append((now+delay,case,down))
    for due,case,down in pending[:]:
     if due<=now:
      command=f'key 1c {down}\n';os.write(control,command.encode());actions.append(dict(seconds=now-start,case=case,command=command.strip()));pending.remove((due,case,down))
    if b'LAT CLI RETURN' in wire and finish is None:finish=now
    if finish is not None and now-finish>2:break
    for bad in [b'RC3 LATENCY FAIL',b'LAT REFUSED:',b'LAT FAIL:',b'IRQ FAIL:',b'Error executing autoexec',b'Guru meditation',b'RST $38 panic']:assert bad not in wire,bad
    assert proc.poll() is None,'frontend exited'
    assert now-last<60,'60s no-wire-progress bound'
    time.sleep(.02)
   else:raise TimeoutError('cell/campaign bound')
 except Exception as e:error=repr(e)
 finally:
  if proc and proc.poll() is None:
   for c in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(c.name))==proc.pid and (c/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():os.kill(int(c.name),signal.SIGTERM)
    except (OSError,PermissionError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  if control is not None:os.close(control)
  (p/'actions.json').write_text(json.dumps(actions,indent=2)+'\n')
 try:
  assert error is None,error
  wire=(p/'last-run/mos-to-vdp.bin').read_bytes();assert b'IRQ PASS: 45 default entries valid; 3 active entries valid.' in wire
  stats=json.loads((p/'last-run/stats.json').read_text());uart=json.loads((p/'last-run/uart.json').read_text())
  assert not any(stats[k] for k in ['failed','unhandled','unregistered','unmapped']);assert uart['tx_drops']==uart['rx_overruns']==0
  reports=p/'reports';reports.mkdir();subprocess.run(['mcopy','-s','-i',str(p/'card.img'),'::/test/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
  proof=oracle.verify(wire,(reports/'R0001.log').read_text(),require_keys=True)
  result=dict(**row,passed=True,proof=proof,elapsed_seconds=time.monotonic()-start)
 except Exception as e:result=dict(**row,passed=False,error=error or repr(e),elapsed_seconds=time.monotonic()-start)
 results.append(result);(root/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
 if not result['passed']:raise SystemExit('Campaign stopped on first unexpected result')
