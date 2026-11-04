"""Assemble the qualified private before/after appliance; never writes an SD."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
root=Path(__file__).resolve().parents[2];base=root/'build/tm001'
build,run,out=(base/n for n in sys.argv[1:4]);info=json.loads((build/'build-info.json').read_text());rows=json.loads((run/'results.json').read_text())
assert len(rows)==8 and all(r['passed'] and not r['physical'] for r in rows)
assert {(r['kind'],r['engine']) for r in rows}=={(k,e) for k in ('startup-original','startup-fixed','uart','perf') for e in ('jit','interp')}
assert all(r['MOS_sha256']==info['baseline_sha256' if r['kind']=='startup-original' else 'fixed_sha256'] for r in rows)
out.mkdir(exist_ok=False);app=out/'appliance';app.mkdir();source=out/'source';source.mkdir()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def copy(a,b):b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def snapshot(a,b):shutil.copytree(a,b,ignore=shutil.ignore_patterns('bin','obj','build','.git','__pycache__'))
original=base/'rc2-001/firmware'
for name,pin,p in (('before',info['baseline_sha256'],original),('fixed',info['fixed_sha256'],build/'fixed')):
 assert h(p/'bin/mos.bin')==pin
 copy(p/'bin/mos.bin',app/f'mos-{name}.bin');copy(p/'bin/mos.map',source/f'mos-{name}.map');snapshot(p,source/('mos-'+name))
for directory in ('before','after'):copy(build/'probe/bin/irqcheck.bin',app/directory/'irqcheck.bin')
for n,dest in (('functional','test.bin'),('example','example.bin'),('perf','perf.bin')):
 record=info['applications'][n];binary=build/n/'bin'/record['binary'];assert h(binary)==record['sha256'];copy(binary,app/'after'/dest);snapshot(build/n,source/n)
copy(build/'functional/checks.bin',app/'after/checks.bin');assert h(build/'functional/checks.bin')==h(build/'perf/checks.bin')
snapshot(build/'probe',source/'probe')
prior=base/'perf2-deploy001/package'
assert h(prior/'vdp-stock.bin')=='b807beef35823b13a0a056f11b7464cd1b1c6356dce0e4098b78ebe059ded35f'
for n in ('mos-stock.bin','vdp-stock.bin'):copy(prior/n,app/n)
copy(root/'LICENSE',app/'licenses/EIRENE-MOS-LICENSE.txt')
for p in prior.iterdir():
 if p.is_file() and ('LICENSE' in p.name or 'CREDITS' in p.name):copy(p,app/'licenses'/p.name)
protocol=root/'docs/tasks/IRQ-001/hardware.txt';copy(protocol,app/'readme.txt')
copy(base/'rc2-001/build-info.json',out/'baseline-build-info.json');copy(build/'build-info.json',out/'build-info.json');copy(build/'linked-checks-r02.json',out/'linked-checks-r02.json');copy(run/'results.json',out/'model-results.json')
(out/'fix.diff').write_bytes(subprocess.check_output(['git','diff',info['baseline_source'],info['source_commit'],'--','src/init.asm'],cwd=root))
(out/'README.md').write_text('# IRQ-001 private before/after test\n\n'+protocol.read_text()+'\nFirmware source: '+info['source_commit']+'; baseline: '+info['baseline_source']+'.\nComplete frozen MOS/probe/functional/example/PERF2 sources are in source/.\nBuild using the unchanged Eirene AgonDev Makefiles; original RC2 toolchain pins\nare retained in baseline-build-info.json. This is upstream\nAgonDev Eirene, not a toolchain migration of official ZDS MOS.\nThe fixed banner deliberately remains RC2: only init.asm changed. The probe\nprints and checks the actual ROM CRC before touching RAM or resetting.\nNo root autoexec, flash utility replacement, SD deployment, hardware execution,\nrelease publication or upstream notification is performed by this packager.\n')
files={str(p.relative_to(app)):dict(bytes=p.stat().st_size,sha256=h(p)) for p in sorted(app.rglob('*')) if p.is_file()}
(app/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+k+'\n' for k,v in files.items()))
(out/'package.json').write_text(json.dumps(dict(source_commit=info['source_commit'],baseline_source=info['baseline_source'],private=True,published=False,deployed=False,Console8_pending=True,files=files,model_cells=8,verified_payload_bytes=sum(r['receiver_bytes'] for r in rows)),indent=2)+'\n')
all_files=[p for p in sorted(out.rglob('*')) if p.is_file()];(out/'SHA256SUMS').write_text(''.join(h(p)+'  '+str(p.relative_to(out))+'\n' for p in all_files));print(out)
