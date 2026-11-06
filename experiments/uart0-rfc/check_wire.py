"""Independent exact wire oracle for RFC001 transfers (no emulator execution)."""
from pathlib import Path
import argparse,json
BASE=0x6af0
SIZES=(1,15,16,17,255,256,257,1024)
def word(n):return n.to_bytes(2,'little')
def command(buf,op,*tail):return b'\x17\x00\xa0'+word(buf)+bytes((op,*tail))
def pattern(n):return bytes((i*157+7)&255 for i in range(n))
def expected_cases():
 footer=command(BASE+2,5,2,0,0,0)
 cases=[]
 for number,size in enumerate(SIZES,1):
  mark=bytes((23,0,128,0x80+number))
  data=command(BASE,2)+command(BASE,0,*word(size))+pattern(size)
  cases.append(dict(case=number,marker=mark,wire=data+footer,borrowed=size,payload=size))
 mark=bytes((23,0,128,0x89));part=command(BASE,0,0,1)+pattern(256)
 data=command(BASE,2)+bytes((23,0,128,0x51))+part*256
 cases.append(dict(case=9,marker=mark,wire=data+footer,borrowed=67588,payload=65536))
 return cases

def verify(wire,require_return=True):
 cursor=0;summary=[]
 for case in expected_cases():
  at=wire.find(case['marker'],cursor)
  if at<0:raise ValueError('Missing case marker '+str(case['case']))
  start=at+len(case['marker']);expected=case['wire'];actual=wire[start:start+len(expected)]
  if actual!=expected:
   mismatch=next((i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),min(len(actual),len(expected)))
   raise ValueError(f"Case {case['case']} differs at byte {mismatch}; truncated/extra/reordered/corrupt source")
  cursor=start+len(expected);summary.append({k:case[k] for k in ('case','borrowed','payload')})
 if b'RFC001 TRANSFER PASS' not in wire[cursor:]:raise ValueError('Missing final PASS')
 if require_return and b'RFC001 CLI RETURN' not in wire[cursor:]:raise ValueError('Missing clean CLI return')
 return dict(passed=True,cases=summary,payload_verified=sum(c['payload'] for c in summary),wire_bytes=len(wire),physical=False)

def selftest():
 rows=expected_cases();wire=b''.join(c['marker']+c['wire'] for c in rows)+b'RFC001 TRANSFER PASS\r\nRFC001 CLI RETURN'
 assert verify(wire)['payload_verified']==67377
 for corrupted in (wire[:50]+wire[51:],wire[:50]+wire[50:51]+wire[50:],wire.replace(b'RFC001 CLI RETURN',b'')):
  try:verify(corrupted)
  except ValueError:pass
  else:raise AssertionError('Oracle accepted corrupted/truncated/unclean return')
 return 'Wire oracle positive/omitted-byte/duplicated-byte/missing-return controls PASS'
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('wire',type=Path,nargs='?');a=p.parse_args()
 print(selftest() if a.wire is None else json.dumps(verify(a.wire.read_bytes()),indent=2))
