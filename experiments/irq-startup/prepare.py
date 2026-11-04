"""Oryx: freeze correction, build twice, retain failing baseline and generate fixtures."""
from pathlib import Path
import hashlib,importlib.util,io,json,os,shlex,shutil,subprocess,sys,tarfile,zlib
root=Path(__file__).resolve().parents[2];base=root/'build/tm001';out=base/sys.argv[1];out.mkdir(exist_ok=False);tool=Path(os.environ['AGONDEV_TOOLCHAIN'])
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root).strip()
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip();raw=subprocess.check_output(['git','archive',commit],cwd=root)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def make(p,name):
 with (out/(name+'.log')).open('w') as f:subprocess.run(['make','AGONDEV_TOOLCHAIN='+str(tool)],cwd=p,stdout=f,stderr=subprocess.STDOUT,check=True)
original=base/'rc2-001/firmware';assert h(original/'bin/mos.bin')=='a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a'
for name in ('fixed','repeat'):
 p=out/name;p.mkdir()
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(p,filter='data')
 make(p,name)
fixed=out/'fixed';assert h(fixed/'bin/mos.bin')==h(out/'repeat/bin/mos.bin')
changes=[str(p.relative_to(fixed/'src')) for p in (fixed/'src').rglob('*') if p.is_file() and h(p)!=h(original/'src'/p.relative_to(fixed/'src'))];assert changes==['init.asm'],changes
objects=[p.name for p in (fixed/'obj').glob('*.o') if h(p)!=h(original/'obj'/p.name)];assert objects==['init.o'],objects
assert (fixed/'bin/mos.bin').stat().st_size==(original/'bin/mos.bin').stat().st_size
# Link full-symbol ELFs in addition to the ordinary flat binaries, then compare.
symbols={}
for name,p in (('original',original),('fixed',fixed)):
 lines=(out/'fixed.log').read_text().splitlines();command=next(shlex.split(l) for l in lines if '/ez80-none-elf-ld ' in l)
 j=command.index('--oformat');command[j+1]='elf32-z80';command[command.index('-o')+1]=str(out/(name+'.elf'));command=[('-Map='+str(out/(name+'.elf.map'))) if a.startswith('-Map=') else a for a in command]
 subprocess.run(command,cwd=p,check=True,stdout=subprocess.DEVNULL)
 subprocess.run([str(tool/'bin/ez80-none-elf-objcopy'),'-O','binary',str(out/(name+'.elf')),str(out/(name+'-from-elf.bin'))],check=True)
 assert h(out/(name+'-from-elf.bin'))==h(p/'bin/mos.bin')
 text=subprocess.check_output([str(tool/'bin/ez80-none-elf-nm'),'-n',str(out/(name+'.elf'))],text=True);s={}
 for line in text.splitlines():
  a=line.split()
  if len(a)>=3:
   try:s[a[-1]]=int(a[0],16)
   except ValueError:pass
 symbols[name]=s;(out/(name+'-symbols.json')).write_text(json.dumps(s,indent=2)+'\n')
for n in ('__2nd_jump_table','__default_mi_handler','_uart0_handler','_vblank_handler','_i2c_handler','_hardReset'):assert symbols['fixed'][n]==symbols['original'][n]
spec=importlib.util.spec_from_file_location('verify',root/'experiments/irq-startup/verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
try:v.verify((original/'bin/mos.bin').read_bytes(),symbols['original'])
except AssertionError as e:bad=dict(accepted=False,reason=str(e))
else:raise AssertionError('Released RC2 incorrectly accepted')
proof=dict(original=bad,fixed=v.verify((fixed/'bin/mos.bin').read_bytes(),symbols['fixed']),mutations=v.mutations((fixed/'bin/mos.bin').read_bytes(),symbols['fixed']))
app=out/'probe';shutil.copytree(root/'experiments/irq-startup/src',app/'src');shutil.copyfile(root/'experiments/irq-startup/Makefile',app/'Makefile');s=symbols['fixed'];baseline_crc=zlib.crc32((original/'bin/mos.bin').read_bytes());fixed_crc=zlib.crc32((fixed/'bin/mos.bin').read_bytes());targets=[s['__default_mi_handler']]*48
for vector,key in ((0x18,'_uart0_handler'),(0x32,'_vblank_handler'),(0x1c,'_i2c_handler')):targets[vector//2]=s[key]
identity=hashlib.sha256(json.dumps(dict(commit=commit,base=baseline_crc,fix=fixed_crc,targets=targets),sort_keys=True).encode()).hexdigest()[:16]
(app/'src/identity.h').write_text(f'#define IRQ_BUILD "{identity}"\n#define IRQ_TABLE {s["__2nd_jump_table"]}UL\n#define DEFAULT_IRQ {s["__default_mi_handler"]}UL\n#define HARD_RESET {s["_hardReset"]}UL\n#define MOS_BYTES {(fixed/"bin/mos.bin").stat().st_size}\n#define BASE_CRC {hex(baseline_crc)}UL\n#define FIX_CRC {hex(fixed_crc)}UL\nstatic const uint24_t expected[48]={{'+','.join(hex(x) for x in targets)+'};\n')
(app/'src/identity.inc').write_text(f'IRQ_TABLE equ {s["__2nd_jump_table"]}\n');make(app,'probe')
# Re-use qualified RC2 app sources and compiled measurement core, updating guards.
release=base/'rc2-001';apps={}
for name,source in (('functional',release/'functional'),('example',release/'example'),('perf',release/'perf/rc2')):
 p=out/name;shutil.copytree(source,p,ignore=shutil.ignore_patterns('bin','obj','__pycache__'))
 if name!='perf':
  ident=p/'src/identity.h';text=ident.read_text();import re
  text=re.sub(r'#define RC_MOS_CRC .*',f'#define RC_MOS_CRC {hex(fixed_crc)}UL',text);text=re.sub(r'#define TM_BUILD .*',f'#define TM_BUILD "{identity}"',text);ident.write_text(text)
 else:
  cfg=p/'src/zz_config.c';text=cfg.read_text().replace(hex(baseline_crc),hex(fixed_crc));text=text.replace('Eirene UART0 RC2','Eirene IRQ startup fix').replace('uart0-rc2','irq-startup-fix');cfg.write_text(text)
 make(p,name)
 if name=='perf':
  for n in ('main.o','platform.o'):assert h(p/'obj'/n)==h(release/'perf/rc2/obj'/n)
 apps[name]=dict(path=str(p),binary='rc2.bin' if name=='perf' else ('test.bin' if name=='functional' else 'example.bin'),sha256=h(p/'bin'/('rc2.bin' if name=='perf' else ('test.bin' if name=='functional' else 'example.bin'))))
info=dict(source_commit=commit,baseline_source='825eaf77176247f5b5ba2f940ae73fcace34e7e5',changes=changes,changed_objects=objects,rebuild_identical=True,bytes=(fixed/'bin/mos.bin').stat().st_size,baseline_crc32=f'{baseline_crc:08X}',fixed_crc32=f'{fixed_crc:08X}',baseline_sha256=h(original/'bin/mos.bin'),fixed_sha256=h(fixed/'bin/mos.bin'),probe_build=identity,probe_sha256=h(app/'bin/irqcheck.bin'),proof=proof,applications=apps)
(out/'build-info.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info))
