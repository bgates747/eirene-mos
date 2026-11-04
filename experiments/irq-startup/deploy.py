"""Archive then replace only the identified Console8 UART appliance."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tarfile
root=Path(__file__).resolve().parents[2];base=root/'build/tm001'
package,out=(base/a for a in sys.argv[1:3]);out.mkdir(exist_ok=False)
mount=Path('/run/media/smith/AGONC8');target=mount/'test/mos-uart0'
def volume():
 fs=json.loads(subprocess.check_output(['findmnt','-J','-o','SOURCE,TARGET,LABEL,UUID,FSTYPE','--mountpoint',str(mount)],text=True))['filesystems'];assert len(fs)==1
 fs=fs[0];assert fs['target']==str(mount) and fs['label']=='AGONC8' and fs['uuid']=='8658-1C23' and fs['fstype']=='vfat',fs
 return fs
fs=volume();assert target.is_dir() and not target.is_symlink()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(d):return {str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=h(p)) for p in sorted(d.rglob('*')) if p.is_file()}
expected=json.loads((package/'package.json').read_text());assert expected['model_cells']==8
subprocess.run(['sha256sum','--check','--status','SHA256SUMS'],cwd=package/'appliance',check=True)
assert h(package/'appliance/mos-before.bin')=='a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a'
assert h(package/'appliance/mos-fixed.bin')=='4550f60e74bb7be7d99e4fd1acaddaf9ac43d5b02a242fadee60c6e92aec30dc'
protected={n:(h(mount/n) if (mount/n).is_file() else None) for n in ('MOS.bin','autoexec.txt','!boot.obey','mos/flash.bin')}
before=manifest(target);shutil.copytree(target,out/'returned');assert manifest(out/'returned')==before
archive=out/'returned.tar.gz'
with tarfile.open(archive,'w:gz') as t:t.add(out/'returned',arcname='returned')
with tarfile.open(archive) as t:
 members=[m for m in t.getmembers() if m.isfile()];assert len(members)==len(before)
 for m in members:
  key=str(Path(m.name).relative_to('returned'));assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==before[key]['sha256']
next_id=int((target/'next.txt').read_text());reports=[int(p.stem[1:]) for p in target.glob('R[0-9][0-9][0-9][0-9].log')]
assert 0<next_id<9990 and (not reports or next_id>max(reports));seeds={'before':next_id,'after':next_id+2}
stage=target.with_name('mos-uart0.stage-irq001');backup=target.with_name('mos-uart0.old-irq001');assert not stage.exists() and not backup.exists()
shutil.copytree(package/'appliance',stage)
for name,record in expected['files'].items():assert h(stage/name)==record['sha256'],name
for folder,number in seeds.items():(stage/folder/'next.txt').write_bytes(f'{number}\r\n'.encode())
text=(stage/'readme.txt').read_text().replace('Prepared only; not deployed. Intended folder:','Directory:')
text=text.replace('I0001.log',f'I{next_id:04}.log')
text=text.replace('Before/after\nhave independent I0001/I0002 startup reports; after has R0003..R0005 plus\nruns.log for UART/performance.',f'Before starts at I{next_id:04}/I{next_id+1:04}; after starts at I{next_id+2:04}/I{next_id+3:04}.\nThen after has R{next_id+4:04}..R{next_id+6:04} plus runs.log for UART/performance.\nBefore/after counters are independent; retries keep/increment their numbers.')
(stage/'readme.txt').write_bytes(text.replace('\n','\r\n').encode())
(stage/'runs.log').write_bytes((f'IRQ-001 staged; not executed. Before next={seeds["before"]}; after next={seeds["after"]}.\r\nPrior UART history is preserved in the project irq001-deploy001/returned.tar.gz.\r\n').encode())
(stage/'deployment.json').write_text(json.dumps(dict(task='IRQ-001',source_commit=expected['source_commit'],source_package=str(package),report_seeds=seeds,prior_reports=reports,prior_archive_sha256=h(archive),physical_tests_pending=True),indent=2)+'\n')
files=manifest(stage);files.pop('SHA256SUMS');(stage/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+n+'\n' for n,v in files.items()))
subprocess.run(['sha256sum','--check','--status','SHA256SUMS'],cwd=stage,check=True)
subprocess.run(['sync','-f',str(stage)],check=True)
assert volume()==fs and manifest(target)==before,'Card identity/content changed before swap'
target.rename(backup)
try:
 stage.rename(target)
 subprocess.run(['sha256sum','--check','--status','SHA256SUMS'],cwd=target,check=True)
 after=manifest(target)
 for n,pin in protected.items():assert (h(mount/n) if (mount/n).is_file() else None)==pin,n
except BaseException:
 if target.exists():shutil.rmtree(target)
 backup.rename(target);raise
shutil.rmtree(backup);subprocess.run(['sync','-f',str(target)],check=True)
receipt=dict(volume=fs,target=str(target),source_commit=expected['source_commit'],archive_sha256=h(archive),archive_verified=True,prior_files=before,prior_reports=reports,report_seeds=seeds,card_files=after,protected_root_files=protected,only_UART_folder_modified=True,physical_firmware_flashed=False,tests_executed=False,remounted=False,ejected=False)
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(h(p)+'  '+str(p.relative_to(out))+'\n' for p in sorted(out.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
print(json.dumps({k:receipt[k] for k in ('target','volume','archive_sha256','prior_reports','report_seeds','only_UART_folder_modified','physical_firmware_flashed')}))
