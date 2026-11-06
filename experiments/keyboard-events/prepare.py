# SPDX-License-Identifier: MIT
"""Freeze the actual selected ring into a standalone native unit fixture; no build/run."""
from pathlib import Path
import argparse,hashlib,json,shutil
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--ring',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args();root=Path(__file__).resolve().parent
out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
shutil.copytree(root/'src',out/'src')
shutil.copyfile(a.ring,out/'src/keyboard_buffer.src')
shutil.copyfile(a.ring.parent/'keyboard_buffer.h',out/'src/keyboard_buffer.h')
shutil.copyfile(root/'Makefile',out/'Makefile')
files={str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.rglob('*')) if f.is_file()}
(out/'source.json').write_text(json.dumps({'ring_source':str(a.ring.resolve()),'files':files,'built':False,'guest_executed':False},indent=2)+'\n')
print(out)
