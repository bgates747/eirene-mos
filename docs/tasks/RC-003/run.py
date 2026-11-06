from pathlib import Path
import importlib.util,json,os,signal,subprocess,sys,time
root=Path('/home/smith/Agon/mystuff/eirene-mos/.emulator/rc003-r01');inputs=root.parents[1]/'build/rc003-runtime-inputs';rows=json.loads((root/'profiles.json').read_text());results=[];campaign=time.monotonic()
spec=importlib.util.spec_from_file_location('oracle',inputs/'check_wire.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle);oracle.selftest()
for row in rows:
 p=Path(row['path']);start=time.monotonic();proc=None;error=None
 try:
  for f in ['.runtime.sha256','.mos-release.sha256']:subprocess.run(['sha256sum','--check','--status',f],cwd=p,check=True)
  subprocess.run(['ssh','-o','BatchMode=yes','raspberrypi','/Agon/mystuff/agon-dev-env/.venv/bin/python','/Agon/mystuff/agon-dev-env/cross-agent/vdplet-rollout/oryx_lease.py','assert-owner','--owner','agon-mos','--lease',sys.argv[1]],check=True,stdout=subprocess.DEVNULL)
  with (p/'frontend.log').open('w') as log:
   proc=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=p,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=row['engine']))
   old=0;last=start;finish=None
   while time.monotonic()-start<300 and time.monotonic()-campaign<1800:
    f=p/'last-run/mos-to-vdp.bin';wire=f.read_bytes() if f.exists() else b''
    if len(wire)!=old:old=len(wire);last=time.monotonic()
    terminal=b'RC3 REFUSED: wrong MOS image' if row['candidate']=='foreign' else b'RC003 CLI RETURN'
    if terminal in wire and finish is None:finish=time.monotonic()
    if finish is not None and time.monotonic()-finish>2:break
    for bad in [b'Guru meditation',b'RST $38 panic',b'IRQ FAIL:',b'IRQ UNSUPPORTED:',b'RC3 TRANSFER FAIL',b'RC1 FAIL',b'RC2 FAIL']:assert bad not in wire,bad
    if row['candidate']!='foreign':assert b'Error executing autoexec' not in wire,'unexpected autoexec failure'
    assert proc.poll() is None,'frontend exited before completion'
    assert time.monotonic()-last<60,'60second no-progress bound'
    time.sleep(.1)
   else:raise TimeoutError('cell/campaign deadline')
 except Exception as e:error=repr(e)
 finally:
  if proc and proc.poll() is None:
   for c in Path('/proc').glob('[0-9]*'):
    try:
     if os.getpgid(int(c.name))==proc.pid and (c/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():os.kill(int(c.name),signal.SIGTERM)
    except (OSError,PermissionError):pass
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
 try:
  assert error is None,error
  wire=(p/'last-run/mos-to-vdp.bin').read_bytes();stats=json.loads((p/'last-run/stats.json').read_text());uart=json.loads((p/'last-run/uart.json').read_text())
  assert not any(stats[k] for k in ['failed','unhandled','unregistered','unmapped']);assert uart['tx_drops']==uart['rx_overruns']==0
  reports=p/'reports';reports.mkdir();subprocess.run(['mcopy','-s','-i',str(p/'card.img'),'::/test/*',str(reports)],check=True,stdout=subprocess.DEVNULL)
  case=row['candidate'];payload=0
  if case=='foreign':
   assert b'RC3 REFUSED: wrong MOS image' in wire and b'RC003 UNEXPECTED FOREIGN ACCEPT' not in wire
   assert not list(reports.glob('R*.log')),'foreign fixture wrote a report'
  else:
   assert b'IRQ PASS: 45 default entries valid; 3 active entries valid.' in wire
   assert b'RC003 CLI RETURN' in wire
   report=(reports/'R0001.log').read_text()
   if case=='rc3':
    assert b'RC3 EXAMPLE PASS' in wire
    assert 'RC3 TRANSFER PASS' in report and 'callbacks=9 expected=9 failed_stage=0' in report
    data=oracle.verify(wire.replace(b'RC003 CLI RETURN',b'RC3 CLI RETURN'));payload=data['payload_verified'];assert payload==67377
   else:
    assert (case.upper()+' PASS') in report and b'EXAMPLE PASS' in wire
    assert 'VERIFY8192 PASS' in report and 'RX-during-TX PASS' in report;payload=8192
  r=dict(**row,passed=True,error=None,payload_verified=payload,elapsed_seconds=time.monotonic()-start)
 except Exception as e:
  r=dict(**row,passed=False,error=error or repr(e),payload_verified=0,elapsed_seconds=time.monotonic()-start)
 results.append(r);(root/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['name','passed','error','payload_verified','elapsed_seconds']}),flush=True)
 if not r['passed']:raise SystemExit('Campaign stopped at first failed cell')
