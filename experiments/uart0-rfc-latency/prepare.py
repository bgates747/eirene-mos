"""Freeze RC3-only latency fixture; no compiler or target execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,zlib
ROOT=Path(__file__).resolve().parents[2]
ROM_SHA='d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out,rom,mosmap):
 assert h(rom)==ROM_SHA,'Only published RC3 is selected'
 text=mosmap.read_text();hits=re.findall(r'^\s*0x([0-9a-f]+)\s+_user_kbvector\s*$',text,re.M);assert len(hits)==1
 app=out/'fixture';shutil.copytree(ROOT/'experiments/uart0-rfc-latency/src',app/'src');shutil.copyfile(ROOT/'experiments/uart0-rfc-latency/Makefile',app/'Makefile')
 spec=importlib.util.spec_from_file_location('packets',ROOT/'experiments/uart0-minimal/packets.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.generate(app);(app/'checks.bin').unlink()
 pins={str(f.relative_to(app)):h(f) for f in sorted(app.rglob('*')) if f.is_file()}
 build=hashlib.sha256(json.dumps(dict(source=pins,rom=ROM_SHA,map=h(mosmap)),sort_keys=True).encode()).hexdigest()[:16]
 (app/'src/identity.h').write_text('#define RFC_BUILD "'+build+'"\n#define RFC_MOS_BYTES 100879u\n#define RFC_MOS_CRC 0xB08C80B8UL\n#define RFC_KB_VECTOR '+hex(int(hits[0],16))+'u\n')
 info=dict(build=build,mos_sha256=ROM_SHA,map_sha256=h(mosmap),source=pins)
 (out/'source.json').write_text(json.dumps(info,indent=2)+'\n');return info
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--mos',type=Path,required=True);a.add_argument('--map',type=Path,required=True);v=a.parse_args();print(json.dumps(prepare(v.out.resolve(),v.mos.resolve(),v.map.resolve()),indent=2))
