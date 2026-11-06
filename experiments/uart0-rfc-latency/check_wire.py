"""Independent packet and retained-report oracle, not a target simulator."""
from pathlib import Path
import argparse,json,re
PAUSES=(0,1,4,8)
PATTERN=bytes((i*157+7)&255 for i in range(8192))
def expected(pauses):
 data=b'\x17\0\x80\x51'+bytes((23,0,195))*pauses+bytes((23,0,160,240,106,2))
 for b in range(32):data+=bytes((23,0,160,240,106,0,0,1))+PATTERN[b*256:(b+1)*256]
 return data+b'\x17\0\x80\x5f'
def rows(text):
 return [{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',line)} for line in text.splitlines() if line.startswith('LAT case=')]
def verify(wire,report,require_keys=False):
 data=rows(report);assert len(data)==8,('eight report cases required',len(data));cursor=0;total=0
 for n,row in enumerate(data,1):
  mode=(n-1)%2;pause=PAUSES[(n-1)//2];assert (row['case'],row['mode'],row['pause'])==(n,mode,pause)
  packet=expected(pause);count=row['packets'];assert 0<count<100
  assert row['payload']==count*8192 and row['wire']==count*len(packet)
  assert row['callbacks']==(count if mode else 0)
  assert 72000<=row['ticks']<144000 and row['irq_count']>0 and 0<row['irq_gap']<60000 and row['fore_gap']<60000
  assert row['coalesced']<=row['keys']
  if require_keys:assert row['keys']>0,('no actual key delivery',n)
  marker=f'LAT BEGIN case={n} mode={mode} pause={pause};'.encode();begin=wire.index(marker,cursor)
  start=wire.index(b'\x17\0\x80\x74',begin)+4
  end=start+count*len(packet);assert wire[start:end]==packet*count,('wire corrupt/truncated/reordered',n)
  trailer=wire[end:wire.index(b'LAT case=',end)]
  assert trailer==b'',('unexpected extra output/bytes before data row',n,trailer[:30])
  cursor=end;total+=count*8192
 assert report.count('VERIFY8192 PASS')==8
 for token in ['Comparator wrong-byte FAIL / correct-byte PASS','LAT RESTORE PASS:','RC3 LATENCY PASS']:assert token in report,token
 assert b'LAT CLI RETURN' in wire[cursor:],'no actual CLI return'
 assert 'RC3 LATENCY FAIL' not in report
 return dict(passed=True,cases=data,payload_wire_verified=total,receiver_final_buffers_verified=8,physical=False,keyboard_cases=sum(r['keys']>0 for r in data))
def selftest():
 wire=b'';lines=['Comparator wrong-byte FAIL / correct-byte PASS'];at=0
 for n in range(1,9):
  mode=(n-1)%2;pause=PAUSES[(n-1)//2];p=expected(pause)
  wire+=f'LAT BEGIN case={n} mode={mode} pause={pause}; one-second window'.encode()+b'\x17\0\x80\x74'+p
  if n==1:at=len(wire)-len(p)+80
  line=f'LAT case={n} mode={mode} pause={pause} packets=1 payload=8192 wire={len(p)} ticks=72000 vtime=100 callbacks={mode} irq_count=900 irq_gap=80 fore_gap=80 keys=2 coalesced=0 key_age=20 cts_low_samples=0 early_rx_samples=1'
  wire+=line.encode();lines.extend([line,'VERIFY8192 PASS'])
 report='\n'.join(lines+['LAT RESTORE PASS: vectors','RC3 LATENCY PASS']);wire+=b'LAT CLI RETURN'
 assert verify(wire,report,True)['payload_wire_verified']==65536
 bads=[(wire[:at]+wire[at+1:],report),(wire[:at]+wire[at:at+1]+wire[at:],report),(wire,report.replace('callbacks=1','callbacks=0',1)),(wire,report.replace('LAT RESTORE PASS:','MISSING:')),(wire.replace(b'LAT CLI RETURN',b''),report)]
 for w,r in bads:
  try:verify(w,r,True)
  except (AssertionError,ValueError):pass
  else:raise AssertionError('negative accepted')
 return 'PASS: exact repeated packets, omissions, duplicates, callback count, restoration and CLI controls'
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('wire',type=Path,nargs='?');a.add_argument('report',type=Path,nargs='?');a.add_argument('--require-keys',action='store_true');v=a.parse_args()
 print(selftest() if v.wire is None else json.dumps(verify(v.wire.read_bytes(),v.report.read_text(),v.require_keys),indent=2))
