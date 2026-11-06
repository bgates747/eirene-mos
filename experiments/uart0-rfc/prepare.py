"""Generate the RC3 fixture from an identified RC3 ROM/map; no compile or run."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil,zlib
ROOT=Path(__file__).resolve().parents[2]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare(out,mos,mosmap):
 data=mos.read_bytes();text=mosmap.read_text()
 if 'uart0_async_send' not in text or 'fill_uart0_tx_fifo' not in text or re.search(r'\buart0_async_write\b',text):raise ValueError('Expected RFC25 map, not RC1/RC2')
 out.mkdir(parents=True,exist_ok=False);app=out/'fixture';shutil.copytree(ROOT/'experiments/uart0-rfc/src',app/'src');shutil.copyfile(ROOT/'experiments/uart0-rfc/Makefile',app/'Makefile')
 spec=importlib.util.spec_from_file_location('packets',ROOT/'experiments/uart0-minimal/packets.py');packets=importlib.util.module_from_spec(spec);spec.loader.exec_module(packets);packets.generate(app);(app/'checks.bin').unlink()
 values={}
 for key,name in {'RFC_IRQ_TABLE':'__2nd_jump_table','RFC_UART_ISR':'_uart0_handler','RFC_VBLANK_ISR':'_vblank_handler','RFC_I2C_ISR':'_i2c_handler'}.items():
  matches=re.findall(r'^\s*0x([0-9a-f]+)\s+'+name+r'\s*$',text,re.M)
  if len(matches)!=1:raise ValueError('Expected one map symbol: '+name)
  values[key]=int(matches[0],16)
 pins={str(p.relative_to(app)):h(p) for p in sorted(app.rglob('*')) if p.is_file()}
 build=hashlib.sha256(json.dumps(dict(source=pins,mos=h(mos),symbols=values),sort_keys=True).encode()).hexdigest()[:16]
 (app/'src/identity.h').write_text('#define RFC_BUILD "'+build+'"\n#define RFC_MOS_BYTES '+str(len(data))+'u\n#define RFC_MOS_CRC '+hex(zlib.crc32(data))+'UL\n'+''.join('#define '+k+' '+hex(v)+'u\n' for k,v in values.items()))
 info=dict(build=build,mos_bytes=len(data),mos_sha256=h(mos),map_sha256=h(mosmap),mos_crc32=f'{zlib.crc32(data):08X}',source=pins,symbols=values)
 (out/'source.json').write_text(json.dumps(info,indent=2)+'\n');return info
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--mos',type=Path,required=True);p.add_argument('--map',type=Path,required=True);a=p.parse_args();print(json.dumps(prepare(a.out.resolve(),a.mos.resolve(),a.map.resolve()),indent=2))
