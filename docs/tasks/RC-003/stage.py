from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess
root=Path('/home/smith/Agon/mystuff/eirene-mos');inputs=root/'build/rc003-runtime-inputs';out=root/'.emulator/rc003-r01';out.mkdir(parents=True,exist_ok=False)
template=root/'.emulator/rfc001-first001/functional-jit';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('api',inputs/'flexe_profile.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
info=json.loads((inputs/'build-info.json').read_text());rows=[]
for candidate,engine in [('rc1','jit'),('rc2','jit'),('rc3','jit'),('rc3','interp'),('foreign','jit')]:
 name=candidate+'-'+engine;p=out/name;p.mkdir();(p/'sdcard').mkdir();mos='rc2' if candidate=='foreign' else candidate
 for f in ['flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf']:(p/f).symlink_to((template/f).resolve())
 for f in ['flexe-agon-emulator','.bespoke-vdp-profile']:shutil.copyfile(template/f,p/f)
 (p/'flexe-agon-emulator').chmod(0o755)
 for suffix,dst in [('bin','mos_platform.bin'),('map','mos_platform.map')]:shutil.copyfile(inputs/mos/('mos.'+suffix),p/dst)
 (p/'.mos-release').write_text('RC003 '+name+' model checks only\n');(p/'.mos-release.sha256').write_text(''.join(h(p/f)+'  '+f+'\n' for f in ['mos_platform.bin','mos_platform.map']))
 with (p/'card.img').open('xb') as f:f.truncate(32*1024*1024)
 subprocess.run(['mkfs.fat','-F','16',str(p/'card.img')],check=True,stdout=subprocess.DEVNULL);subprocess.run(['mmd','-i',str(p/'card.img'),'::/test'],check=True)
 app='rc3' if candidate=='foreign' else candidate
 for f in ['test.bin','example.bin','checks.bin']:
  if (inputs/app/f).exists():subprocess.run(['mcopy','-i',str(p/'card.img'),str(inputs/app/f),'::/test/'+f],check=True)
 subprocess.run(['mcopy','-i',str(p/'card.img'),str(inputs/'irqcheck.bin'),'::/test/irqcheck.bin'],check=True)
 cmds='CD /test\r\n'+('test\r\nECHO RC003 UNEXPECTED FOREIGN ACCEPT\r\n' if candidate=='foreign' else 'irqcheck\r\ntest\r\nexample\r\nECHO RC003 CLI RETURN\r\n')
 (p/'autoexec.txt').write_bytes(cmds.encode());subprocess.run(['mcopy','-i',str(p/'card.img'),str(p/'autoexec.txt'),'::/autoexec.txt'],check=True)
 (p/'sdcard.img').symlink_to('card.img');api.name_flexe_profile(p);api.verify_profile_executables(p/'flexe-agon-emulator',p/'flexe-agon-emulator.bin')
 files=['flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf','mos_platform.bin','mos_platform.map','flexe-agon-emulator']
 pins={f:h(p/f) for f in files};(p/'.runtime.sha256').write_text(''.join(v+'  '+f+'\n' for f,v in pins.items()))
 for f in ['.runtime.sha256','.mos-release.sha256']:subprocess.run(['sha256sum','--check','--status',f],cwd=p,check=True)
 assert pins['mos_platform.bin']==info['candidates'][mos]['sha256'];assert pins['flexe-agon-emulator.bin']=='7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01'
 rows.append(dict(name=name,candidate=candidate,engine=engine,path=str(p),pins=pins))
(out/'profiles.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'profiles':[x['name'] for x in rows]}))
