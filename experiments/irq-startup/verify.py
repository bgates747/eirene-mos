"""Check final linked startup bytes; mutation tests must reject broken ordering."""
import json
from pathlib import Path

def verify(image,s):
 start=s['___bss_start'];length=s['___bss_len'];table=s['__2nd_jump_table']
 assert length>0 and start<=table and table+192<=start+length,'Table/BSS range'
 begin=s['__init'];end=s['__init_default_vectors'];code=image[begin:end]
 addr=lambda x:x.to_bytes(3,'little')
 clear=b'\x21'+addr(start)+b'\x11'+addr(start+1)+b'\x01'+addr(length-1)+b'\x36\x00\xcd'+addr(s['ldir_handle_zerolen'])
 call=b'\xcd'+addr(end)
 assert code.count(clear)==1,'Expected exactly one final BSS clear'
 assert code.count(call)==1,'Expected exactly one default initialization'
 assert code.index(call)==code.index(clear)+len(clear),'Defaults must follow final BSS clear'
 return dict(table=table,bytes=192,slots=48,BSS_start=start,BSS_bytes=length,clear_address=begin+code.index(clear),init_call=begin+code.index(call))

def mutations(image,s):
 good=verify(image,s);a=good['init_call'];b=good['clear_address'];call=image[a:a+4];out=[]
 candidates={
  'missing-call':image[:a]+b'\0'*4+image[a+4:],
  'early-call':image[:b]+call+image[b+4:a]+b'\0'*4+image[a+4:],
  'duplicate-call':image[:s['__init']]+call+image[s['__init']+4:],
  'malformed-clear':image[:b]+b'\0'+image[b+1:]
 }
 for name,data in candidates.items():
  try:verify(data,s)
  except AssertionError as e:out.append(dict(name=name,rejected=True,reason=str(e)))
  else:raise AssertionError('Mutation accepted: '+name)
 bad=dict(s);bad['__2nd_jump_table']=s['___bss_start']+s['___bss_len']-191
 try:verify(image,bad)
 except AssertionError as e:out.append(dict(name='table-overruns-BSS',rejected=True,reason=str(e)))
 else:raise AssertionError('Bad range accepted')
 return out
