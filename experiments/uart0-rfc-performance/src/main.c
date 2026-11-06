/* Original source-only RC3 matched throughput/remaining-work preparation. */
#include <agon/mos.h>
#include <ez80f92.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "packets.h"
#include "rom_crc.h"
#include "platform.h"
#define BULK_ONLY 0
#define BULK_WORK 1
#define PACED_WORK 2
static uint8_t packet[8454],checks[960],file,live,failed;
static unsigned report,packet_bytes,payload_bytes;
static volatile uint8_t *sv;
static uint32_t state,units;
static char line[512];
static void send(const uint8_t*p,unsigned n){mos_puts((const char*)p,n,0);}
static int record(const char*s){puts(s);unsigned n=strlen(s);return mos_fwrite(file,(char*)s,n)==n&&mos_fwrite(file,"\r\n",2)==2;}
#include "run_counter.inc"
static int report_open(void){
 unsigned n=first_report();char name[16];if(!n)return 0;
 for(;n<10000;n++){
  snprintf(name,sizeof name,"R%04u.log",n);uint8_t f=mos_fopen(name,FA_READ);
  if(f){mos_fclose(f);continue;}
  file=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);if(!file)return 0;
  if(!save_next_report(n+1)){mos_fclose(file);file=0;return 0;}
  report=n;return 1;
 }return 0;
}
static void work(void){uint32_t x=state;x^=x<<13;x^=x>>17;x^=x<<5;state=x;units++;}
/* A timeout marks data invalid but cannot cancel a live borrowed source. */
static int drain(unsigned useful){
 uint32_t start=pf_ticks();
 while(live&&!pf_done){if(useful)work();if(pf_ticks()-start>5*PF_HZ)failed=1;}
 while(!(IO(UART0_LSR)&0x40)){if(useful)work();if(pf_ticks()-start>5*PF_HZ)failed=1;}
 live=0;return !failed&&!(IO(UART0_IER)&2);
}
static int gp(const uint8_t*p,unsigned n,uint8_t expected){
 sv[sysvar_gp]=0xfe;send(p,n);uint32_t start=pf_ticks();
 while(sv[sysvar_gp]!=expected)if(pf_ticks()-start>5*PF_HZ)return 0;
 return 1;
}
static void fill(unsigned payload){
 unsigned n=0;payload_bytes=payload;
 memcpy(packet+n,(uint8_t[]){23,0,160,240,106,2},6);n+=6;
 for(unsigned at=0;at<payload;at+=256){
  memcpy(packet+n,(uint8_t[]){23,0,160,240,106,0,0,1},8);n+=8;
  for(unsigned j=0;j<256;j++)packet[n++]=(uint8_t)((at+j)*157+7);
 }
 packet_bytes=n;
}
static int verify(void){
 send(v_reset_flag,sizeof v_reset_flag);
 for(unsigned base=0;base<payload_bytes;base+=64){
  for(unsigned i=0;i<64;i++){
   unsigned at=base+i;
   const uint8_t c[]={23,0,160,241,106,6,0x23,240,106,(uint8_t)at,(uint8_t)(at>>8),244,106,(uint8_t)at,(uint8_t)(at>>8)};
   memcpy(checks+i*15,c,15);
  }
  send(checks,sizeof checks);if(!gp(v_reply,sizeof v_reply,0))return 0;
 }
 snprintf(line,sizeof line,"VERIFY payload=%u PASS",payload_bytes);return record(line);
}
static int calibrate(unsigned rep){
 const uint8_t fence[]={23,0,128,0x75};
 snprintf(line,sizeof line,"PERF CAL BEGIN rep=%u window=%lu",rep,(unsigned long)PF_WINDOW);if(!record(line))return 0;
 if(!gp(fence,sizeof fence,0x75)||!drain(0))return 0;
 state=0x12345678UL;units=0;pf_gap_reset();uint32_t start=pf_ticks(),vstart=getsysvar_time();
 while(pf_ticks()-start<PF_WINDOW)work();
 uint32_t elapsed=pf_ticks()-start,vtime=getsysvar_time()-vstart,gap=pf_max_poll_gap;
 if(!units||gap>=60000)return 0;
 snprintf(line,sizeof line,"PERF CAL rep=%u ticks=%lu vtime=%lu work=%lu credited=%lu state=%08lX gap=%lu",rep,(unsigned long)elapsed,(unsigned long)vtime,(unsigned long)units,(unsigned long)(units-1),(unsigned long)state,(unsigned long)gap);
 return record(line);
}
static int trial(unsigned rep,unsigned scenario,unsigned mode){
 unsigned paced=scenario==PACED_WORK,useful=scenario!=BULK_ONLY;
 fill(paced?256:8192);
 snprintf(line,sizeof line,"PERF BEGIN rep=%u scenario=%u mode=%u window=%lu payload_packet=%u wire_packet=%u",rep,scenario,mode,(unsigned long)PF_WINDOW,payload_bytes,packet_bytes);
 if(!record(line))return 0;
 const uint8_t fence[]={23,0,128,0x75};if(!gp(fence,sizeof fence,0x75)||!drain(0))return 0;
 state=0x12345678UL;units=0;unsigned packets=0,missed=0;uint24_t cb_before=pf_callbacks;
 uint32_t due=0,remainder=0,call_ticks=0,release_ticks=0,max_late=0;
 pf_gap_reset();uint32_t start=pf_ticks(),vstart=getsysvar_time();
 do{
  if(paced)while(pf_ticks()-start<due)work();
  uint32_t now=pf_ticks()-start;if(paced&&now>due&&now-due>max_late)max_late=now-due;
  uint32_t before=pf_ticks();
  if(mode){
   pf_source=packet;pf_length=packet_bytes;pf_done=0;live=1;pf_submit();
  }else send(packet,packet_bytes);
  call_ticks+=pf_ticks()-before;
  while(live&&!pf_done){if(useful)work();if(pf_ticks()-before>5*PF_HZ)failed=1;}
  /* Source release permits the next immutable packet. No per-packet TEMT. */
  live=0;release_ticks+=pf_ticks()-before;packets++;
  if(paced){remainder+=256UL*PF_HZ;due+=remainder/44100UL;remainder%=44100UL;if(pf_ticks()-start>due)missed++;}
  if(failed)break;
 }while(paced?due<PF_WINDOW:pf_ticks()-start<PF_WINDOW);
 if(paced)while(pf_ticks()-start<PF_WINDOW)work();
 uint32_t tail=pf_ticks();int ok=drain(useful);tail=pf_ticks()-tail;
 uint32_t elapsed=pf_ticks()-start,vtime=getsysvar_time()-vstart,gap=pf_max_poll_gap;
 unsigned callbacks=(unsigned)(pf_callbacks-cb_before);
 if(callbacks!=(mode?packets:0)||gap>=60000||elapsed>PF_WINDOW+5*PF_HZ)ok=0;
 snprintf(line,sizeof line,"PERF DATA rep=%u scenario=%u mode=%u packets=%u payload=%lu wire=%lu ticks=%lu vtime=%lu call=%lu release=%lu tail=%lu work=%lu credited=%lu state=%08lX late=%lu missed=%u callbacks=%u gap=%lu",
  rep,scenario,mode,packets,(unsigned long)packets*payload_bytes,(unsigned long)packets*packet_bytes,(unsigned long)elapsed,(unsigned long)vtime,(unsigned long)call_ticks,(unsigned long)release_ticks,(unsigned long)tail,(unsigned long)units,(unsigned long)(units?units-1:0),(unsigned long)state,(unsigned long)max_late,missed,callbacks,(unsigned long)gap);
 if(!record(line)||!ok)return 0;
 return gp(fence,sizeof fence,0x75)&&verify();
}
int main(void){
 if(installed_crc(RFC_MOS_BYTES)!=RFC_MOS_CRC||pf_context()||IO(UART0_IER)&2){puts("PERF REFUSED: exact RC3/foreground ADL/MBASE0/EI/idle sender required");return 1;}
 putch(12);puts("RC3 UART THROUGHPUT AND REMAINING-WORK TEST");
 puts(PF_DURATION);puts("A stall is FAIL; report the last progress line. No firmware is flashed.");
 sv=mos_sysvars();if(!report_open())return 1;
 int clock=pf_clock_start(),ok=clock;
 if(!clock){record("PERF FAIL: PRT1 active/IRQ-owned or source readback failed");mos_fclose(file);return 1;}
 snprintf(line,sizeof line,"PERF3 build=%s kind=%s MOS=B08C80B8 report=R%04u tick_hz=72000 window=%lu repeats=%u",PF_BUILD,PF_KIND,report,(unsigned long)PF_WINDOW,PF_REPEATS);ok=record(line);
 if(ok)ok=record("POLICY same immutable packet; source release between packets, TEMT at timed end; no per-packet receiver fence");
 if(ok){send(v_setup,sizeof v_setup);ok=gp(v_mismatch_probe,sizeof v_mismatch_probe,1)&&gp(v_match_probe,sizeof v_match_probe,0);}
 if(ok)ok=record("Comparator wrong-byte FAIL / correct-byte PASS");
 for(unsigned rep=1;ok&&rep<=PF_REPEATS;rep++){
  ok=calibrate(rep);
  for(unsigned slot=0;ok&&slot<6;slot++){
   unsigned cell=(slot+2*(rep-1))%6;ok=trial(rep,cell/2,(cell%2)^((rep-1)&1));
  }
 }
 while((live&&!pf_done)||(IO(UART0_IER)&2)||!(IO(UART0_LSR)&0x40))pf_ticks(); /* Retain live source/code; no cancellation. */
 if(!pf_clock_stop())ok=0;
 send(v_cleanup,sizeof v_cleanup);
 if(ok)ok=record("PERF RESTORE PASS: timer1 disabled/source restored; vectors and keyboard untouched");
 record("LIMIT: reload write-only; next owner configures it. PRT polling requires gaps<65536ticks. Work capacity is not exclusive ISR CPU percent.");
 record(ok?"PERF3 DATA COMPLETE":"PERF3 FAIL");mos_fclose(file);return ok?0:1;
}
