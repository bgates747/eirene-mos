"""Oryx only: prepare stopped, private RFC fixture profiles; never launch."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,subprocess
p=argparse.ArgumentParser(description=__doc__)
for key in ('out','build','runtime','template','profile-api','rc2','rc2-map'):p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args();out=a.out.resolve();build=a.build.resolve();out.mkdir(parents=True,exist_ok=False)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
info=json.loads((build/'build-proof.json').read_text());assert h(build/'fixture/bin/test.bin')==info['app_sha256']
files=('flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf')
pins={'flexe-agon-emulator.bin':'7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01','flexe-vdp.so':'0866265bd6f3d73ad572f31dc1bb954f308ed9a5d857efa9414d37e1ade13374','esp32-firmware.bin':'201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a'}
runtime=out/'runtime';runtime.mkdir()
for name in files:
 if name in pins:assert h(a.runtime/name)==pins[name],name
 shutil.copyfile(a.runtime/name,runtime/name)
(runtime/files[0]).chmod(0o755)
spec=importlib.util.spec_from_file_location('profile_api',a.profile_api);api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
assert h(a.rc2)=='a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a'
rows=[]
for kind,engine in (('functional','jit'),('functional','interp'),('refusal','jit')):
 profile=out/(kind+'-'+engine);profile.mkdir();(profile/'sdcard').mkdir()
 for name in files:(profile/name).symlink_to('../runtime/'+name)
 mos=build/'mos-rfc.bin' if kind=='functional' else a.rc2
 mosmap=build/'mos.map' if kind=='functional' else a.rc2_map
 shutil.copyfile(mos,profile/'mos_platform.bin');shutil.copyfile(mosmap,profile/'mos_platform.map')
 for name in ('flexe-agon-emulator','.bespoke-vdp-profile'):shutil.copyfile(a.template/name,profile/name)
 (profile/'flexe-agon-emulator').chmod(0o755)
 (profile/'.mos-release').write_text('RFC001 '+kind+'; exact original or explicit foreign-ROM control; off-device only\n')
 (profile/'.mos-release.sha256').write_text(''.join(h(profile/name)+'  '+name+'\n' for name in ('mos_platform.bin','mos_platform.map')))
 with (profile/'card.img').open('xb') as stream:stream.truncate(32*1024*1024)
 subprocess.run(['mkfs.fat','-F','16',str(profile/'card.img')],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['mmd','-i',str(profile/'card.img'),'::/rfc'],check=True)
 subprocess.run(['mcopy','-i',str(profile/'card.img'),str(build/'fixture/bin/test.bin'),'::/rfc/test.bin'],check=True)
 commands='CD /rfc\r\ntest\r\n'+('test\r\nDIR\r\nECHO RFC001 CLI RETURN\r\n' if kind=='functional' else 'ECHO RFC001 UNEXPECTED ACCEPT\r\n')
 (profile/'autoexec.txt').write_bytes(commands.encode())
 subprocess.run(['mcopy','-i',str(profile/'card.img'),str(profile/'autoexec.txt'),'::/autoexec.txt'],check=True)
 (profile/'sdcard.img').symlink_to('card.img');api.name_flexe_profile(profile);api.verify_profile_executables(profile/'flexe-agon-emulator',profile/'flexe-agon-emulator.bin')
 names=(*files,'mos_platform.bin','mos_platform.map','flexe-agon-emulator')
 (profile/'.runtime.sha256').write_text(''.join(h(profile/name)+'  '+name+'\n' for name in names))
 subprocess.run(['bash','-n',str(profile/'flexe-agon-emulator')],check=True)
 for pin in ('.runtime.sha256','.mos-release.sha256'):subprocess.run(['sha256sum','--check','--status',pin],cwd=profile,check=True)
 assert not list(profile.glob('fab-agon-emulator*'))
 rows.append(dict(path=str(profile),kind=kind,engine=engine,mos_sha256=h(profile/'mos_platform.bin'),stopped=True))
result=dict(schema='RFC001-stopped-profiles-1',build=info['build'],app_sha256=info['app_sha256'],runtime={name:h(runtime/name) for name in files},profile_api_sha256=h(a.profile_api),profiles=rows)
(out/'profiles.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
