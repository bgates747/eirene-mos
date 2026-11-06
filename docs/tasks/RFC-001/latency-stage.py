"""Oryx private stopped profiles; no guest or firmware execution."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess
root=Path('/home/smith/Agon/mystuff/eirene-mos');inputs=root/'build/rfc001/lat001-inputs';out=root/'.emulator/rfc001-lat001';out.mkdir(exist_ok=False)
template=root/'.emulator/rc003-r01/rc3-jit'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('api',inputs/'flexe_profile.py');api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
assert h(inputs/'mos.bin')=='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50'
rows=[]
for engine in ['jit','interp']:
 p=out/engine;p.mkdir();(p/'sdcard').mkdir()
 for f in ['flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf']:(p/f).symlink_to((template/f).resolve())
 for f in ['flexe-agon-emulator','.bespoke-vdp-profile']:shutil.copyfile(template/f,p/f)
 (p/'flexe-agon-emulator').chmod(0o755)
 for a,b in [('mos.bin','mos_platform.bin'),('mos.map','mos_platform.map')]:shutil.copyfile(inputs/a,p/b)
 (p/'.mos-release').write_text('Published RC3 B08C80B8; LAT1 private functional model run\n')
 (p/'.mos-release.sha256').write_text(''.join(h(p/f)+'  '+f+'\n' for f in ['mos_platform.bin','mos_platform.map']))
 with (p/'card.img').open('xb') as f:f.truncate(32*1024*1024)
 subprocess.run(['mkfs.fat','-F','16',str(p/'card.img')],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['mmd','-i',str(p/'card.img'),'::/test'],check=True)
 for f in ['test.bin','irqcheck.bin']:subprocess.run(['mcopy','-i',str(p/'card.img'),str(inputs/f),'::/test/'+f],check=True)
 (p/'autoexec.txt').write_bytes(b'CD /test\r\nirqcheck\r\ntest\r\nECHO LAT CLI RETURN\r\n')
 subprocess.run(['mcopy','-i',str(p/'card.img'),str(p/'autoexec.txt'),'::/autoexec.txt'],check=True)
 (p/'sdcard.img').symlink_to('card.img');api.name_flexe_profile(p);api.verify_profile_executables(p/'flexe-agon-emulator',p/'flexe-agon-emulator.bin')
 donor=Path('/home/smith/Agon/mystuff/AgonJukebox/docs/tasks/UART-004')
 assert h(donor/'capture_shim.c')==h(inputs/'capture_shim.c'),'input shim source differs from retained donor'
 shutil.copyfile(donor/'capture_shim.so',p/'capture_shim.so')
 files=['flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf','mos_platform.bin','mos_platform.map','capture_shim.so']
 pins={f:h(p/f) for f in files};(p/'.runtime.sha256').write_text(''.join(v+'  '+f+'\n' for f,v in pins.items()))
 assert pins['flexe-agon-emulator.bin']=='7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01'
 rows.append(dict(engine=engine,path=str(p),pins=pins,shim_source=h(inputs/'capture_shim.c')))
(out/'profiles.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
