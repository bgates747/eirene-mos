"""Oryx only, owned FIFO lease required: finite original RFC functional cells."""
from pathlib import Path
import argparse,importlib.util,json,os,shlex,shutil,signal,subprocess,time
p=argparse.ArgumentParser(description=__doc__);p.add_argument('profiles',type=Path);p.add_argument('--lease',required=True);a=p.parse_args()
root=a.profiles.resolve().parent;config=json.loads(a.profiles.read_text());results=[]
spec=importlib.util.spec_from_file_location('wire_oracle',Path(__file__).with_name('check_wire.py'));oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
def lease():
 command=['/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/vdplet-rollout/oryx_lease.py','assert-owner','--owner','agon-mos','--lease',a.lease]
 subprocess.run(['ssh','-o','BatchMode=yes','raspberrypi',shlex.join(command)],check=True,stdout=subprocess.DEVNULL)
campaign=time.monotonic()
for row in config['profiles']:
 profile=Path(row['path']);resultdir=profile/'results';resultdir.mkdir(exist_ok=False);proc=None;error=None;start=time.monotonic();last=start;size=0
 try:
  if start-campaign>=900:raise TimeoutError('900s total campaign bound')
  for pin in ('.runtime.sha256','.mos-release.sha256'):subprocess.run(['sha256sum','--check','--status',pin],cwd=profile,check=True)
  with (resultdir/'frontend.log').open('w') as log:
   lease() # immediately before this actual emulator process
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=row['engine']),start_new_session=True)
   while time.monotonic()-start<300 and time.monotonic()-campaign<900:
    f=profile/'last-run/mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
    if len(wire)!=size:size=len(wire);last=time.monotonic()
    if row['kind']=='functional':
     if b'RFC001 CLI RETURN' in wire:break
     if b'RFC001 TRANSFER FAIL' in wire or b'RFC001 REFUSED' in wire:raise AssertionError('Original RFC functional fixture failed/refused')
     if b'Error executing autoexec' in wire:raise AssertionError('Unexpected MOS command failure')
    else:
     if b'RFC001 REFUSED: wrong MOS image' in wire and b'Error executing autoexec.txt at line 2' in wire:break
     if b'RFC001 UNEXPECTED ACCEPT' in wire:raise AssertionError('Foreign ROM accepted')
    if b'Guru meditation' in wire or b'RST $38 panic' in wire:raise AssertionError('Guest panic')
    if proc.poll() is not None:raise AssertionError('Frontend exited early')
    if time.monotonic()-last>=60:raise TimeoutError('60s without UART progress')
    time.sleep(.1)
   else:raise TimeoutError('300s cell / 900s campaign bound')
 except Exception as exc:error=repr(exc)
 finally:
  if proc and proc.poll() is None:
   expected=(profile/'flexe-agon-emulator.bin').resolve()
   for entry in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(entry.name))==proc.pid and (entry/'exe').resolve()==expected:os.kill(int(entry.name),signal.SIGTERM)
    except (OSError,PermissionError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
  if (profile/'last-run').exists():shutil.copytree(profile/'last-run',resultdir/'raw')
  (resultdir/'reports').mkdir()
  subprocess.run(['mcopy','-s','-i',str(profile/'card.img'),'::/rfc/*',str(resultdir/'reports')],check=True,stdout=subprocess.DEVNULL)
 try:
  if error:raise AssertionError(error)
  wire=(resultdir/'raw/mos-to-vdp.bin').read_bytes()
  if row['kind']=='functional':
   # Prove BOTH repeated invocations, including their full source/reuse streams.
   parts=wire.split(b'UART0 RFC TRANSFER CHECK')
   if len(parts)!=3:raise AssertionError('Expected exactly two application invocations')
   checks=[]
   for i,part in enumerate(parts[1:],1):
    # The second actual invocation proves first returned; final ECHO proves second.
    checked=oracle.verify(part,require_return=i==2);checks.append(checked)
    report=(resultdir/'reports'/f'R{i:04}.log').read_text()
    if report.count('CASE ')!=9 or 'callbacks=9 expected=9 failed_stage=0' not in report or 'RFC001 TRANSFER PASS' not in report:raise AssertionError('Incomplete callback/case/report proof')
   if (resultdir/'reports/next.txt').read_text().strip()!='3':raise AssertionError('Sequential report counter mismatch')
   (resultdir/'wire-proof.json').write_text(json.dumps(dict(invocations=checks,payload_verified=sum(c['payload_verified'] for c in checks)),indent=2)+'\n')
  else:
   if list((resultdir/'reports').glob('R*.log')) or b'Case 1/9' in wire:raise AssertionError('Refusal touched report/transfer state')
  stats=json.loads((resultdir/'raw/stats.json').read_text());uart=json.loads((resultdir/'raw/uart.json').read_text())
  if any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')) or uart['tx_drops'] or uart['rx_overruns']:raise AssertionError('Backend or UART error counter')
 except Exception as exc:
  if error is None:error=repr(exc)
 result=dict(**row,passed=error is None,error=error,elapsed_seconds=time.monotonic()-start,physical=False)
 (resultdir/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result);(root/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(result),flush=True)
 if error:raise SystemExit('Campaign stopped at first unexpected failure; retain original evidence')
