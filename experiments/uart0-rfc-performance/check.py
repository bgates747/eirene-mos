"""Independent measured-work/report/packet oracle; no target execution."""
from pathlib import Path
import argparse,json,re
MASK=(1<<32)-1
SEED=0x12345678
def step(x):
 x^=(x<<13)&MASK;x^=x>>17;x^=(x<<5)&MASK;return x&MASK
def advance(n):
 def apply(columns,value):
  result=0
  while value:
   bit=value&-value;result^=columns[bit.bit_length()-1];value-=bit
  return result
 value=SEED;columns=[step(1<<i) for i in range(32)]
 while n:
  if n&1:value=apply(columns,value)
  n>>=1
  if n:columns=[apply(columns,x) for x in columns]
 return value
def packet(payload):
 out=bytes((23,0,160,240,106,2))
 for at in range(0,payload,256):out+=bytes((23,0,160,240,106,0,0,1))+bytes(((at+j)*157+7)&255 for j in range(256))
 return out
def fields(line):return {k:int(v,16 if k=='state' else 10) for k,v in re.findall(r'(\w+)=(\w+)',line) if k not in ['build','kind','MOS','report']}
def verify(text,wire=None):
 header=next(l for l in text.splitlines() if l.startswith('PERF3 build='));config=fields(header)
 kind=re.search(r'kind=(\w+)',header).group(1);assert kind in ['full','smoke']
 repeats,window=(3,720000) if kind=='full' else (1,14400)
 assert config['tick_hz']==72000 and config['window']==window and config['repeats']==repeats
 cal={};data=[]
 for l in text.splitlines():
  if l.startswith('PERF CAL rep='):cal[fields(l)['rep']]=fields(l)
  if l.startswith('PERF DATA '):data.append(fields(l))
 assert len(cal)==repeats and set(cal)==set(range(1,repeats+1))
 assert [(d['rep'],d['scenario'],d['mode']) for d in data]==[(r,((slot+2*(r-1))%6)//2,((slot+2*(r-1))%2)^((r-1)&1)) for r in range(1,repeats+1) for slot in range(6)]
 summaries=[];cursor=0
 for c in cal.values():
  assert window<=c['ticks']<=window+72000 and 1<c['work']<2**32 and c['credited']==c['work']-1
  assert c['state']==advance(c['work']) and c['gap']<60000
 for d in data:
  assert d['ticks']>=window and d['ticks']<=window+5*72000 and d['gap']<60000
  payload=256 if d['scenario']==2 else 8192;p=packet(payload);n=d['packets'];assert 0<n<=(window+5*72000)*115200//(72000*len(p))+2
  assert d['payload']==payload*n and d['wire']==len(p)*n
  assert d['callbacks']==(n if d['mode'] else 0)
  assert d['state']==advance(d['work']) and d['credited']==max(0,d['work']-1)
  assert d['call']<=d['release'] and d['release']<=d['ticks'] and d['tail']<=d['ticks']
  if d['scenario']==0:assert d['work']==0
  if d['scenario']==2:assert n==(window*44100+256*72000-1)//(256*72000)
  if wire is not None:
   marker=f"PERF BEGIN rep={d['rep']} scenario={d['scenario']} mode={d['mode']} ".encode();begin=wire.index(marker,cursor);start=wire.index(bytes((23,0,128,0x75)),begin)+4;end=start+n*len(p)
   assert wire[start:end]==p*n,'actual wire packet corruption'
   assert wire[end:end+9]==b'PERF DATA','unexpected extra output before data row';cursor=end
  c=cal[d['rep']];retained=None if d['scenario']==0 else (d['credited']/d['ticks'])/(c['credited']/c['ticks'])
  summaries.append(dict(**d,payload_bytes_per_second=d['payload']*72000/d['ticks'],wire_bytes_per_second=d['wire']*72000/d['ticks'],retained_work_percent=None if retained is None else retained*100,foregone_capacity_percent=None if retained is None else (1-retained)*100))
 assert text.count('VERIFY payload=8192 PASS')==4*repeats and text.count('VERIFY payload=256 PASS')==2*repeats
 for marker in ['Comparator wrong-byte FAIL / correct-byte PASS','PERF RESTORE PASS:','PERF3 DATA COMPLETE']:assert marker in text,marker
 assert 'PERF3 FAIL' not in text
 if wire is not None:assert b'PERF CLI RETURN' in wire[cursor:]
 return dict(valid=True,kind=kind,target_executed_by_oracle=False,physical_provenance_asserted=False,rows=summaries)
def selftest():
 x=SEED
 for n in range(100):assert advance(n)==x;x=step(x)
 lines=['PERF3 build=hostcontrol kind=smoke MOS=B08C80B8 report=R0001 tick_hz=72000 window=14400 repeats=1','Comparator wrong-byte FAIL / correct-byte PASS',f'PERF CAL rep=1 ticks=14400 vtime=20 work=10000 credited=9999 state={advance(10000):08X} gap=10']
 wire=b''
 for slot in range(6):
  scenario,mode=slot//2,slot%2;n=35 if scenario==2 else 2;payload=256 if scenario==2 else 8192;work=0 if scenario==0 else 5000;p=packet(payload)
  wire+=f'PERF BEGIN rep=1 scenario={scenario} mode={mode} '.encode()+bytes((23,0,128,0x75))+p*n
  line=f'PERF DATA rep=1 scenario={scenario} mode={mode} packets={n} payload={n*payload} wire={n*len(p)} ticks=14450 vtime=20 call=10 release=100 tail=5 work={work} credited={max(work-1,0)} state={advance(work):08X} late=1 missed=0 callbacks={n if mode else 0} gap=500'
  wire+=line.encode();lines.extend([line,f'VERIFY payload={payload} PASS'])
 text='\n'.join(lines+['PERF RESTORE PASS:','PERF3 DATA COMPLETE']);wire+=b'PERF CLI RETURN';assert verify(text,wire)['valid']
 bads=[(text.replace('state=12345678','state=00000000',1),wire),(text.replace('callbacks=2','callbacks=3',1),wire),(text.replace('PERF DATA rep=1 scenario=0 mode=0','MISSING',1),wire),(text,wire[:100]+wire[101:]),(text,wire[:100]+wire[100:101]+wire[100:])]
 for t,w in bads:
  try:verify(t,w)
  except (AssertionError,StopIteration,ValueError):pass
  else:raise AssertionError('corruption accepted')
 return 'PASS: independent xorshift jump, full case/order/state/callback/count rules, omitted/duplicated wire negatives'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('report',type=Path,nargs='?');p.add_argument('--wire',type=Path);a=p.parse_args()
 print(selftest() if a.report is None else json.dumps(verify(a.report.read_text(),a.wire.read_bytes() if a.wire else None),indent=2))
