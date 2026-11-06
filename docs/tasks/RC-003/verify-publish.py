from pathlib import Path
import hashlib,json,subprocess,urllib.request,zipfile
r=Path('/Agon/mystuff/eirene-mos');p=r/'docs/tasks/RC-003';meta=json.loads((p/'packages.json').read_text());out=r/'build/rc003/downloaded';out.mkdir();receipts={}
for c,v in meta.items():
 release=json.loads(subprocess.check_output(['gh','api','repos/bgates747/eirene-mos/releases/tags/'+v['tag']],text=True));assert release['prerelease'] and not release['draft']
 assert release['body']==(p/(c+'-release-notes.md')).read_text()
 for a in release['assets']:
  f=out/a['name']
  with urllib.request.urlopen(a['browser_download_url'],timeout=45) as src:f.write_bytes(src.read())
  local=r/'build/rc003/packages'/a['name'];assert f.read_bytes()==local.read_bytes()
  if f.suffix=='.zip':
   assert hashlib.sha256(f.read_bytes()).hexdigest()==v['zip_sha256']
   with zipfile.ZipFile(f) as z:assert z.testzip() is None
 # Check annotated tag points to exactly the chosen source commit.
 commit=subprocess.check_output(['gh','api','repos/bgates747/eirene-mos/commits/'+v['tag'],'--jq','.sha'],text=True).strip();assert commit==v['commit']
 receipts[c]={'release':release,'tag_commit_verified':commit,'downloaded_byte_exact':True,'zip_sha256':v['zip_sha256'],'model_verified':True,'new_hardware_run':False}
 print(json.dumps({'candidate':c,'verified':release['html_url'],'assets_byte_exact':True}),flush=True)
before=json.loads((p/'original-releases.json').read_text())
for old,new in [('3.1.0_uart0_rc_1','3.1.0_uart0_rc_1.1'),('3.1.0_uart0_rc_2','3.1.0_uart0_rc_2.1')]:
 original=before[old]
 note='> **SUPERSEDED: interrupt-table startup bug.** This original image initializes interrupt defaults before clearing BSS, erasing 45 defaults. Use the startup-corrected ['+new+'](https://github.com/bgates747/eirene-mos/releases/tag/'+new+') for the same ABI. Original tag and downloadable assets are preserved for historical reproduction. See [startup PR #3](https://github.com/AgonPlatform/eirene-mos/pull/3).\n\n---\n\n'+original['body']
 f=out/(old+'-notice.json');f.write_text(json.dumps({'body':note}))
 subprocess.run(['gh','api','--method','PATCH','repos/bgates747/eirene-mos/releases/'+str(original['id']),'--input',str(f)],check=True,stdout=subprocess.DEVNULL)
 current=json.loads(subprocess.check_output(['gh','api','repos/bgates747/eirene-mos/releases/tags/'+old],text=True))
 assert current['body']==note
 assert [(x['id'],x['name'],x['size'],x.get('digest')) for x in current['assets']]==[(x['id'],x['name'],x['size'],x.get('digest')) for x in original['assets']]
receipts['original_refs_before']=(p/'original-refs.txt').read_text()
refs=subprocess.check_output(['git','-C',str(r),'ls-remote','origin','refs/heads/main','refs/tags/3.1.0_uart0_rc_1','refs/tags/3.1.0_uart0_rc_2'],text=True);assert refs==receipts['original_refs_before'];receipts['main_and_original_tags_unchanged']=True;receipts['original_assets_unchanged']=True;receipts['original_release_descriptions_notice_only']=True
(p/'publication.json').write_text(json.dumps(receipts,indent=2)+'\n');print('All three releases verified; original tags/assets/main preserved; original descriptions gained notices only.')
