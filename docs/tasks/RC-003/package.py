from pathlib import Path
import hashlib,json,shutil,tarfile,zipfile
ROOT=Path('/Agon/mystuff/eirene-mos');B=ROOT/'build/rc003';N=B/'native-r02';TASK=ROOT/'docs/tasks/RC-003';E=B/'evidence';E.mkdir(exist_ok=True)
with tarfile.open('/tmp/rc003-results.tar.gz') as t:t.extractall(E,filter='data')
rows=json.loads((E/'results.json').read_text());assert len(rows)==5 and all(x['passed'] for x in rows)
info=json.loads((N/'build-info.json').read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sum(x['payload_verified'] for x in rows)==151138
pub=B/'packages';pub.mkdir(exist_ok=False)
ignore=shutil.ignore_patterns('bin','obj','build','__pycache__','*.o','.git')
allmeta={}
for c,tag,label in [('rc1','3.1.0_uart0_rc_1.1','RC1.1'),('rc2','3.1.0_uart0_rc_2.1','RC2.1'),('rc3','3.1.0_uart0_rc_3','RC3')]:
 data=info['candidates'][c];p=pub/tag;p.mkdir()
 shutil.copytree(N/c,p/'source',ignore=ignore)
 functional=N/'apps'/c/('fixture' if c=='rc3' else 'functional');example=N/'apps'/c/'example'
 shutil.copytree(functional,p/'fixture',ignore=ignore);shutil.copytree(example,p/'example',ignore=ignore)
 for src,dst in [(N/c/'bin/mos.bin','mos-'+label.lower()+'.bin'),(N/c/'bin/mos.map','mos-'+label.lower()+'.map'),(N/c/'bin/mos.elf','mos-'+label.lower()+'.elf'),(functional/'bin/test.bin','test.bin'),(example/'bin/example.bin','example.bin'),(ROOT/'docs/tasks/IRQ-001/attachment/irqcheck.bin','irqcheck.bin'),(ROOT/'docs/tasks/IRQ-001/attachment/irqcheck.asm','irqcheck.asm')]:shutil.copyfile(src,p/dst)
 if (functional/'checks.bin').exists():shutil.copyfile(functional/'checks.bin',p/'checks.bin')
 # Freeze the tested target library/headers, not compiler executables or an invented SDK release version.
 (p/'sdk/lib').mkdir(parents=True);shutil.copyfile(B/'toolchain/lib/libagon.a',p/'sdk/lib/libagon.a');shutil.copytree(B/'toolchain/include',p/'sdk/include')
 (p/'sdk/NOTICE.txt').write_text('''Unchanged target SDK dependency from the AgonDev distribution used for original RC1/RC2.
libagon.a SHA256 04e340186590810dd490d01655b50baaca557b7764006598890e845e6fc1252c.
This is NOT the current nightly or v0.22 target library. No SDK version is invented.
AgonDev: Jeroen Venema; AgDev: Paul Cawte; CE Programming contributors.
CRT source credits Paul Cawte, CE Toolchain and Dean Belfield; individual source/header notices apply.
Official SDK sources: https://github.com/AgonPlatform/agondev
Compiler executables are not bundled. The SDK components are not relicensed as original test code.
Retained notices including nanoprintf 0BSD are in ../licenses/CREDITS.txt and the included headers.
''')
 licenses=p/'licenses';shutil.copytree(ROOT/'build/tm001/rc2-001/3.1.0_uart0_rc_2/licenses',licenses)
 shutil.copyfile(ROOT/'LICENSE',licenses/'EIRENE-MOS-LICENSE.txt');shutil.copyfile(ROOT/'docs/tasks/IRQ-001/attachment/LICENSE.txt',licenses/'MINIMAL-CHECKER-LICENSE.txt')
 (licenses/'RC3-CREDITS.txt').write_text('Prepared by Codex on behalf of Brandon. Original MOS: Dean Belfield, Lennart Benschop and Agon contributors. Eirene and RFC25 UART sender: Tom Morton. AgonDev: Jeroen Venema; AgDev: Paul Cawte; CE Programming contributors. Original source copyright/license notices remain authoritative and are retained.\n')
 evidence=p/'evidence';evidence.mkdir();selected=[x for x in rows if x['candidate']==c or (c=='rc3' and x['candidate']=='foreign')]
 for x in selected:shutil.copytree(E/x['name'],evidence/x['name'])
 (evidence/'model-results.json').write_text(json.dumps(selected,indent=2)+'\n')
 if c=='rc2':shutil.copytree(ROOT/'docs/tasks/IRQ-001/hardware-reports',evidence/'prior-console8');shutil.copyfile(ROOT/'docs/tasks/IRQ-001/hardware-results.md',evidence/'prior-console8-results.md')
 (p/'source-commit.txt').write_text(data['commit']+'\n');(p/'build-info.json').write_text(json.dumps(dict(candidate=data,applications=info['apps'][c],toolchain=info['toolchain'],libagon_sha256=info['libagon_sha256']),indent=2)+'\n')
 (p/'source/.source-commit').write_text(data['commit']+'\n')
 compatible='42h/43h; preserves the original '+('guarded RC1' if c=='rc1' else 'lean RC2')+' transport contract' if c!='rc3' else '25h; BREAKING CHANGE from RC2 — 42h/43h are absent'
 scope=('The exact MOS image also matches the earlier Console8-qualified startup-fixed RC2 image byte for byte. The new fixture/example identities were model-tested here.' if c=='rc2' else 'These exact new candidate bits were model-tested; no new physical run is claimed.')
 warning=('''**BREAKING ABI CHANGE FROM RC2:** syscall25h replaces42h/43h. Existing RC2 apps must migrate or use RC2.1. RC3 retains Tom\'s one-positive-immutable-source/non-null assembly callback/actualMB0/ADL/EI contract. It has no queue, BUSY/NULL protection, cancellation or finish syscall. Ignore the raw RFC\'s IER-derived A return; its comment incorrectly promises A=0. CTS is checked per FIFO refill and may spin inside the ISR under DI. A blocked receiver can therefore delay RX, keyboard, VBlank and timers.

**THE PINNED RFC HAS THE STARTUP BUG:** [RFC2](https://github.com/AgonPlatform/eirene-mos/pull/2) revision ffab9c9c84a31535d1ec976b7e6f23b2579ecb80 initializes its interrupt defaults before clearing BSS, erasing45 defaults. This RC3 includes the separate [PR3 correction](https://github.com/AgonPlatform/eirene-mos/pull/3). It is a fork integration candidate, not an upstream release or RFC acceptance.
''' if c=='rc3' else '''**STARTUP-CORRECTED REFRESH.** The original '''+label[:3]+''' release erased45 default interrupt entries after initializing them. This revision changes only src/init.asm and init.o; sender code, ABI, size and on-screen branding remain unchanged. Identify the corrected firmware by the filename and CRC below. The original tag/assets remain historical downloads.
''')
 readme=f'''# Eirene MOS 3.1.0 UART0 {label}

Applications can calculate while MOS sends their buffer to the VDP. This fork
prerelease fixes startup so unused interrupt entries retain their proper defaults.

{warning}
Source tag: `{tag}`. Exact source commit: `{data['commit']}`.
MOS: `{data['bytes']}` bytes; CRC32 `{data['crc32']}`;
SHA256 `{data['sha256']}`. API: {compatible}.

## Install and run

Use stock Bistromathics VDP 2.16.0 or its compatible ordinary buffered-command
implementation. No custom VDP commands or modified VDP firmware are required.
Keep your normal known-good recovery firmware available. From this directory:

```text
flash mos mos-{label.lower()}.bin
```

Let the normal updater finish and reboot. Return to this directory and type,
without switches:

```text
irqcheck
test
example
```

Expect `IRQ PASS`, {('`RC3 TRANSFER PASS`' if c=='rc3' else '`'+c.upper()+' PASS`')},
and an `EXAMPLE PASS` line, followed by normal return to MOS. `test` clears the
screen and prints progress. Allow about two minutes; if it takes longer,
something is wrong. Report the last line; a stall is not PASS. Sequential
Rnnnn.log reports preserve repeated runs and do not depend on the Agon clock.

## Build and adapt

`source/` is the full matching MOS source snapshot; `fixture/` is the generated
matching test source, and `example/` is the complete worked application recipe.
`irqcheck.asm` is an independent single-file read-only startup checker.
Install the existing AgonDev compiler (LLVM15.0.7, c76386c0083e6a6236ff774275227e2389f85538).
The exact target SDK library and headers used here are frozen under `sdk/`;
newer SDK libraries change the binary. From this package root:

```sh
pkg=$(pwd)
make -C source AGONDEV_TOOLCHAIN="$AGONDEV_TOOLCHAIN" LIBDIR="$pkg/sdk/lib" INCLUDEDIR="$pkg/sdk/include"
make -C fixture AGONDEV_TOOLCHAIN="$AGONDEV_TOOLCHAIN" LIBDIR="$pkg/sdk/lib" INCLUDEDIR="$pkg/sdk/include"
make -C example AGONDEV_TOOLCHAIN="$AGONDEV_TOOLCHAIN" LIBDIR="$pkg/sdk/lib" INCLUDEDIR="$pkg/sdk/include"
```

MOS output is `source/bin/mos.bin`; application outputs are `fixture/bin/test.bin`
and `example/bin/example.bin`. Every included file is pinned in SHA256SUMS and
manifest.json. The firmware branch retains Eirene's upstream AgonDev compiler;
this does not change the separate official ZDS II MOS toolchain.

A source buffer must remain immutable until its callback releases it. Source
release, transmitter-empty (UART0 LSR bit6/TEMT), and VDP command execution are
separate events. Serialize ordinary output and application exit after physical
drain; retain receiver inputs until the relevant normal VDP reply/fence.
Study the matching example and caller contract before adapting it. RC1.1/RC2.1
use43h finish; RC3's tiny assembly callback posts a prearmed flag and the C
foreground polls TEMT after release. Callback code stays resident through exit.

## What was checked

Startup, the matching UART regression, and the worked example passed on Flexe.
RC3 ran with both JIT and interpreter, including nine valid sources per run,
67377 receiver-verified payload bytes per run, concurrent RX, source reuse,
and a wrong-ROM refusal control. RC1.1/RC2.1 each verified8192 bytes on JIT.
All backend error and UART drop/overrun counters were zero. Exact raw records
are in evidence/. These are functional tests, not new throughput, CPU-headroom,
audio-deadline, indefinite-stall or physical CTS-margin results. {scope}

Original copyright/license notices and Agon/SDK attribution are in source/ and
licenses/. Tests/packaging are prepared by Codex on behalf of Brandon. Main,
original release tags/assets and independent EMOS installations remain unchanged.
'''
 # Normalize incidental compact prose without touching code/identifiers.
 for before,after in [('syscall25h','syscall 25h'),('replaces42h','replaces 42h'),('erasing45','erasing 45'),('erased45','erased 45'),('43h finish','43h finish'),('verified8192','verified 8192'),('LLVM15','LLVM 15')]:readme=readme.replace(before,after)
 (p/'README.md').write_text(readme)
 files={str(f.relative_to(p)):{'bytes':f.stat().st_size,'sha256':h(f)} for f in sorted(p.rglob('*')) if f.is_file()}
 (p/'manifest.json').write_text(json.dumps(dict(tag=tag,label=label,source_commit=data['commit'],firmware=data,files=files,model_only=c!='rc2',published=False),indent=2)+'\n')
 (p/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+n+'\n' for n,v in files.items())+h(p/'manifest.json')+'  manifest.json\n')
 z=pub/(tag+'.zip')
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED) as archive:
  for f in sorted(p.rglob('*')):
   if f.is_file():archive.write(f,str(f.relative_to(p)))
 with zipfile.ZipFile(z) as archive:
  assert archive.testzip() is None
  for n,v in files.items():assert hashlib.sha256(archive.read(n)).hexdigest()==v['sha256']
  assert hashlib.sha256(archive.read('mos-'+label.lower()+'.bin')).hexdigest()==data['sha256']
 sha=pub/(tag+'.zip.sha256');sha.write_text(h(z)+'  '+z.name+'\n')
 allmeta[c]=dict(tag=tag,label=label,commit=data['commit'],zip_name=z.name,zip_bytes=z.stat().st_size,zip_sha256=h(z),sha256_name=sha.name,MOS=data,files=len(files),model_cases=[x['name'] for x in selected])
(TASK/'packages.json').write_text(json.dumps(allmeta,indent=2)+'\n');(TASK/'build-info.json').write_text(json.dumps(info,indent=2)+'\n');(TASK/'model-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({k:{n:v[n] for n in ['tag','zip_bytes','zip_sha256','files']} for k,v in allmeta.items()},indent=2))
