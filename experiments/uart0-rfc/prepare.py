"""Freeze a reproducible RFC functional fixture; no compile/run/deployment."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,shutil,zlib,re
ROOT=Path(__file__).resolve().parents[2]
PIN='ffab9c9c84a31535d1ec976b7e6f23b2579ecb80'
SHA='f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbol(text,name):
 found=re.findall(r'^\s*0x([0-9a-f]+)\s+'+re.escape(name)+r'\s*$',text,re.M)
 if len(found)!=1:raise ValueError('Expected one map symbol: '+name)
 return int(found[0],16)
def prepare(out,mos,mosmap):
 data=mos.read_bytes()
 if len(data)!=100824 or hashlib.sha256(data).hexdigest()!=SHA:raise ValueError('Not exact original RFC ROM')
 if digest(mosmap)!='765cd95b92be8dc3cb3cbe4ee087be22bc21d466a53b9be242245914aee3c169':raise ValueError('RFC map pin mismatch')
 out.mkdir(parents=True,exist_ok=False);app=out/'fixture'
 shutil.copytree(ROOT/'experiments/uart0-rfc/src',app/'src');shutil.copyfile(ROOT/'experiments/uart0-rfc/Makefile',app/'Makefile')
 spec=importlib.util.spec_from_file_location('packets',ROOT/'experiments/uart0-minimal/packets.py');packets=importlib.util.module_from_spec(spec);spec.loader.exec_module(packets);packets.generate(app)
 (app/'checks.bin').unlink() # This fixture constructs comparator queries itself.
 names={'RFC_IRQ_TABLE':'__2nd_jump_table','RFC_UART_ISR':'_uart0_handler','RFC_VBLANK_ISR':'_vblank_handler','RFC_I2C_ISR':'_i2c_handler'}
 values={key:symbol(mosmap.read_text(),value) for key,value in names.items()}
 files={str(p.relative_to(app)):digest(p) for p in sorted(app.rglob('*')) if p.is_file()}
 build=hashlib.sha256(json.dumps(dict(source=files,mos=SHA,symbols=values),sort_keys=True).encode()).hexdigest()[:16]
 (app/'src/identity.h').write_text('#define RFC_BUILD "'+build+'"\n#define RFC_MOS_BYTES '+str(len(data))+'u\n#define RFC_MOS_CRC '+hex(zlib.crc32(data))+'UL\n'+''.join('#define '+k+' '+hex(v)+'u\n' for k,v in values.items()))
 shutil.copyfile(mos,out/'mos-rfc.bin');shutil.copyfile(mosmap,out/'mos.map')
 info=dict(schema='RFC001-source-1',source_commit=PIN,mos_bytes=len(data),mos_sha256=SHA,mos_crc32=f'{zlib.crc32(data):08X}',map_sha256=digest(mosmap),build=build,source=files,generated_header_sha256=digest(app/'src/identity.h'),symbols=values,firmware_modified=False,hardware_qualified=False)
 (out/'source.json').write_text(json.dumps(info,indent=2)+'\n');return info
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--mos',type=Path,required=True);p.add_argument('--map',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.out.resolve(),a.mos.resolve(),a.map.resolve()),indent=2))
