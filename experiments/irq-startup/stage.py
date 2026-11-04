"""Stage eight stopped actual-firmware profiles for the finite IRQ regression."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
root=Path(__file__).resolve().parents[2];base=root/'build/tm001';build=base/sys.argv[1];out=base/sys.argv[2];out.mkdir(exist_ok=False);info=json.loads((build/'build-info.json').read_text())
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();runtime=out/'runtime';shutil.copytree(base/'perf-flexe002/runtime',runtime)
for n,pin in {'flexe-agon-emulator.bin':'7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01','flexe-vdp.so':'0866265bd6f3d73ad572f31dc1bb954f308ed9a5d857efa9414d37e1ade13374','esp32-firmware.bin':'201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a'}.items():assert h(runtime/n)==pin
spec=importlib.util.spec_from_file_location('factory',root.parent/'agon-dev-env/scripts/setup_emulator.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory)
preflight_spec=importlib.util.spec_from_file_location('preflight',Path(sys.argv[3]));preflight=importlib.util.module_from_spec(preflight_spec);preflight_spec.loader.exec_module(preflight)
template=root.parent/'agon-mos/.emulator/uart0-completion-jit-final';rows=[]
for kind in ('startup-original','startup-fixed','uart','perf'):
 firmware=base/'rc2-001/firmware' if kind=='startup-original' else build/'fixed'
 for engine in ('jit','interp'):
  p=out/(kind+'-'+engine);p.mkdir();(p/'sdcard').mkdir();files=('flexe-agon-emulator.bin','flexe-vdp.so','esp32-firmware.bin','esp32-firmware.elf')
  for n in files:(p/n).symlink_to('../runtime/'+n)
  for a,b in (('mos.bin','mos_platform.bin'),('mos.map','mos_platform.map')):shutil.copyfile(firmware/'bin'/a,p/b)
  for n in ('flexe-agon-emulator','.bespoke-vdp-profile'):shutil.copyfile(template/n,p/n)
  (p/'flexe-agon-emulator').chmod(0o755);(p/'.mos-release').write_text('IRQ-001 '+kind+' pinned private regression\n');(p/'.mos-release.sha256').write_text(''.join(h(p/n)+'  '+n+'\n' for n in ('mos_platform.bin','mos_platform.map')))
  with (p/'card.img').open('xb') as f:f.truncate(32*1024*1024)
  subprocess.run(['mkfs.fat','-F','16',str(p/'card.img')],check=True,stdout=subprocess.DEVNULL);subprocess.run(['mmd','-i',str(p/'card.img'),'::/irq'],check=True)
  def put(src,dst):subprocess.run(['mcopy','-i',str(p/'card.img'),str(src),'::/'+dst],check=True)
  if kind.startswith('startup'):
   put(build/'probe/bin/irqcheck.bin','irq/irqcheck.bin');commands='irqcheck\r\n'
  elif kind=='uart':
   put(build/'functional/bin/test.bin','irq/test.bin');put(build/'functional/checks.bin','irq/checks.bin');put(build/'example/bin/example.bin','irq/example.bin');commands='test\r\ntest\r\nexample\r\n'
  else:
   put(build/'perf/bin/rc2.bin','irq/rc2.bin');put(build/'perf/checks.bin','irq/checks.bin');commands='rc2\r\n'
  a=p/'autoexec.txt';a.write_bytes(('CD /irq\r\n'+commands+'DIR\r\nECHO IRQ001 CLI RETURN\r\n').encode());put(a,'autoexec.txt');(p/'sdcard.img').symlink_to('card.img');factory.name_flexe_profile(p)
  preflight.verify_profile_executables(p/'flexe-agon-emulator',p/'flexe-agon-emulator.bin')
  (p/'.runtime.sha256').write_text(''.join(h(p/n)+'  '+n+'\n' for n in (*files,'mos_platform.bin','mos_platform.map','flexe-agon-emulator')))
  rows.append(dict(path=str(p),kind=kind,engine=engine,MOS_sha256=h(p/'mos_platform.bin'),probe_build=info['probe_build'],physical=False))
(out/'profiles.json').write_text(json.dumps(dict(build=str(build),profiles=rows),indent=2)+'\n');print(out)
