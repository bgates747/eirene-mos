# SPDX-License-Identifier: MIT
"""Bounded linked-code property check, not an executed native/keyboard test."""
from pathlib import Path
import re,sys,json
binary,mapfile,expected=sys.argv[1:]
symbols={name:int(addr,16) for addr,name in re.findall(r'^\s*0x([0-9a-fA-F]+)\s+(\S+)\s*$',Path(mapfile).read_text(),re.M)}
image=Path(binary).read_bytes();base=0x40000
start=symbols['kbuf_remove'];end=symbols['_kbuf_clear']
code=image[start-base:end-base]
pattern=rb'\x3c\xe6\x1f\x32...([\xb7\x3c])\xc9$'
match=re.search(pattern,code,re.S);assert match,'unknown linked dequeue tail'
op=match[1][0]
# The actual tail increments and masks the read index, stores it, and then
# OR A (original) or INC A (fix) sets the success flag consumed by the wrappers.
false_empty=[]
for prior in range(32):
    index=(prior+1)&31
    z=(index==0) if op==0xb7 else (((index+1)&255)==0)
    if z:false_empty.append(prior)
assert expected in ('original','corrected')
assert false_empty==([31] if expected=='original' else [])
print(json.dumps({'source_class':expected,'linked_remove_address':hex(start),
                  'post_copy_false_empty_indices':false_empty,'indices_checked':32,
                  'guest_executed':False,'scope':'actual linked dequeue tail only'}))
