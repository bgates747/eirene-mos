"""Freeze short/full callers against the same exact RC3; no compiler/run."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil
ROOT=Path(__file__).resolve().parents[2]
ROM='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out,rom,mosmap):
 assert h(rom)==ROM and 'uart0_async_send' in mosmap.read_text()
 out.mkdir(parents=True,exist_ok=False);cases=[]
 for name,window,repeats in [('full',720000,3),('smoke',14400,1)]:
  app=out/name;shutil.copytree(ROOT/'experiments/uart0-rfc-performance/src',app/'src');shutil.copyfile(ROOT/'experiments/uart0-rfc-performance/Makefile',app/'Makefile')
  if name=='smoke':(app/'Makefile').write_text((app/'Makefile').read_text().replace('NAME = test','NAME = smoke'))
  s=importlib.util.spec_from_file_location('packets',ROOT/'experiments/uart0-minimal/packets.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p);p.generate(app);(app/'checks.bin').unlink()
  pins={str(f.relative_to(app)):h(f) for f in sorted(app.rglob('*')) if f.is_file()}
  build=hashlib.sha256(json.dumps(dict(source=pins,mos=ROM,map=h(mosmap),window=window,repeats=repeats),sort_keys=True).encode()).hexdigest()[:16]
  duration='Allow about five minutes. If longer than six minutes, something is wrong.' if name=='full' else 'SHORT INSTRUMENTATION CHECK ONLY; allow about one minute. No full-window performance claim.'
  (app/'src/identity.h').write_text(f'#define PF_BUILD "{build}"\n#define PF_KIND "{name}"\n#define PF_WINDOW {window}UL\n#define PF_REPEATS {repeats}u\n#define PF_DURATION "{duration}"\n#define RFC_MOS_BYTES 100879u\n#define RFC_MOS_CRC 0xB08C80B8UL\n')
  cases.append(dict(kind=name,build=build,window=window,repeats=repeats,source=pins))
 info=dict(mos_sha256=ROM,map_sha256=h(mosmap),cases=cases);(out/'source.json').write_text(json.dumps(info,indent=2)+'\n');return info
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--mos',type=Path,required=True);a.add_argument('--map',type=Path,required=True);v=a.parse_args();print(json.dumps(prepare(v.out.resolve(),v.mos.resolve(),v.map.resolve()),indent=2))
