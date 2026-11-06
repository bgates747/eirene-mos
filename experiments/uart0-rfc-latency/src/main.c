/* RC3 normal finite receiver backpressure, not a firmware modification. */
#include <agon/mos.h>
#include <ez80f92.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "packets.h"
#include "rom_crc.h"
#include "platform.h"
static uint8_t packet[8500],checks[960],file;
static volatile uint8_t *sv;
static uint32_t max_key_age,max_fore_gap,last_fore;
static unsigned report,source_bytes;
static uint24_t cts_blocked,rx_early;
static uint8_t live,failed;
static char line[512];
static void send(const uint8_t*p,unsigned n){mos_puts((const char*)p,n,0);}
static int record(const char*s){puts(s);unsigned n=strlen(s);return mos_fwrite(file,(char*)s,n)==n&&mos_fwrite(file,"\r\n",2)==2;}
#include "run_counter.inc"
static int report_open(void){
 unsigned n=first_report();char name[16];
 if(!n)return 0;
 for(;n<10000;n++){
  snprintf(name,sizeof name,"R%04u.log",n);uint8_t f=mos_fopen(name,FA_READ);
  if(f){mos_fclose(f);continue;}
  file=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);if(!file)return 0;
  if(!save_next_report(n+1)){mos_fclose(file);file=0;return 0;}
  report=n;return 1;
 }return 0;
}
static uint32_t service(void){
 uint32_t now=ticks(),gap=now-last_fore;last_fore=now;if(gap>max_fore_gap)max_fore_gap=gap;
 uint24_t age=lat_key_poll();if(age>max_key_age)max_key_age=age;
 if(!(IO(UART0_MSR)&0x10))cts_blocked++;
 if(sv[sysvar_gp]==0x51)rx_early++;
 return now;
}
static int idle(void){
 uint32_t start=ticks();
 while(!(IO(UART0_LSR)&0x40))if(service()-start>5*TICK_HZ)failed=1;
 live=0;return !failed&&!(IO(UART0_IER)&2);
}
static int gp(const uint8_t*p,unsigned n,uint8_t expected){
 sv[sysvar_gp]=0xfe;send(p,n);uint32_t t=ticks();
 while(sv[sysvar_gp]!=expected)if(service()-t>5*TICK_HZ)return 0;
 return 1;
}
static void make_packet(unsigned pauses){
 unsigned n=0;
 memcpy(packet+n,(uint8_t[]){23,0,128,0x51},4);n+=4;
 for(unsigned i=0;i<pauses;i++){memcpy(packet+n,(uint8_t[]){23,0,195},3);n+=3;}
 memcpy(packet+n,(uint8_t[]){23,0,160,240,106,2},6);n+=6;
 for(unsigned b=0;b<32;b++){
  memcpy(packet+n,(uint8_t[]){23,0,160,240,106,0,0,1},8);n+=8;
  for(unsigned j=0;j<256;j++)packet[n++]=(uint8_t)((b*256+j)*157+7);
 }
 memcpy(packet+n,(uint8_t[]){23,0,128,0x5f},4);n+=4;source_bytes=n;
}
static int verify(void){
 send(v_reset_flag,sizeof v_reset_flag);
 for(unsigned base=0;base<8192;base+=64){
  for(unsigned i=0;i<64;i++){
   unsigned at=base+i;
   const uint8_t c[]={23,0,160,241,106,6,0x23,240,106,(uint8_t)at,(uint8_t)(at>>8),244,106,(uint8_t)at,(uint8_t)(at>>8)};
   memcpy(checks+i*15,c,15);
  }
  send(checks,sizeof checks);if(!gp(v_reply,sizeof v_reply,0))return 0;
 }
 return record("VERIFY8192 PASS");
}
static int trial(unsigned mode,unsigned pauses,unsigned number){
 make_packet(pauses);
 snprintf(line,sizeof line,"LAT BEGIN case=%u mode=%u pause=%u; one-second window, then byte check",number,mode,pauses);
 if(!record(line))return 0;
 const uint8_t fence[]={23,0,128,0x74};if(!gp(fence,sizeof fence,0x74)||!idle())return 0;
 tx_callbacks=0;max_key_age=max_fore_gap=0;cts_blocked=rx_early=0;
 last_fore=ticks();clocks_run();uint32_t start=ticks(),vstart=getsysvar_time();unsigned packets=0;
 do{
  sv[sysvar_gp]=0xfe;
  if(mode){
   tx_source=packet;tx_length=source_bytes;tx_done=0;live=1;lat_submit();
   while(!tx_done)if(service()-start>10*TICK_HZ)failed=1;
  }else{send(packet,source_bytes);service();}
  if(!idle())return 0;
  packets++;
 }while(service()-start<TICK_HZ&&!failed);
 uint32_t end=service(),vtime=getsysvar_time()-vstart;clocks_pause();
 uint24_t irqs=irq_count,max_irq=irq_max_gap,keys=key_count,coal=key_coalesced;
 if(tx_callbacks!=(mode?packets:0)||!irqs||end-start>2*TICK_HZ||max_fore_gap>=60000||max_irq>=60000)failed=1;
 snprintf(line,sizeof line,"LAT case=%u mode=%u pause=%u packets=%u payload=%lu wire=%lu ticks=%lu vtime=%lu callbacks=%u irq_count=%u irq_gap=%u fore_gap=%lu keys=%u coalesced=%u key_age=%lu cts_low_samples=%u early_rx_samples=%u",
  number,mode,pauses,packets,(unsigned long)packets*8192,(unsigned long)packets*source_bytes,(unsigned long)(end-start),(unsigned long)vtime,(unsigned)tx_callbacks,(unsigned)irqs,(unsigned)max_irq,(unsigned long)max_fore_gap,(unsigned)keys,(unsigned)coal,(unsigned long)max_key_age,(unsigned)cts_blocked,(unsigned)rx_early);
 if(!record(line)||failed)return 0;
 if(!keys&&!record("KEYBOARD NOT TESTED: no key event delivered in this window"))return 0;
 if(!gp(fence,sizeof fence,0x74)||!verify())return 0;
 return record("LAT CASE PASS");
}
int main(void){
 if(installed_crc(RFC_MOS_BYTES)!=RFC_MOS_CRC||lat_context()){
  puts("LAT REFUSED: requires exact RC3, foreground ADL/MBASE0/EI");return 1;
 }
 if(*(volatile uint24_t*)RFC_KB_VECTOR){puts("LAT REFUSED: existing keyboard callback owns input");return 1;}
 putch(12);puts("RC3 UART RESPONSIVENESS TEST\nAllow about two minutes; if longer, something is wrong.\nEight sync/async cases. Optional: tap keys during each one-second window.\nA stall is FAIL; report the last progress line and reset. No firmware is flashed.");
 sv=mos_sysvars();if(!report_open())return 1;
 int clock=clocks_start(),ok=clock;
 if(!clock){record("LAT FAIL: timer already active");mos_fclose(file);return 1;}
 mos_setkbvector(lat_keyboard,0);
 snprintf(line,sizeof line,"LAT1 build=%s MOS=B08C80B8 report=R%04u tick_hz=72000 interval_limit=65535; model timing is not hardware timing",RFC_BUILD,report);ok=record(line);
 if(ok)ok=record("Clock PRT1 polling; PRT2 nominal1ms IRQ. Keyboard age starts at MOS callback delivery, not physical keypress.");
 if(ok){send(v_setup,sizeof v_setup);ok=gp(v_mismatch_probe,sizeof v_mismatch_probe,1)&&gp(v_match_probe,sizeof v_match_probe,0);}
 if(ok)ok=record("Comparator wrong-byte FAIL / correct-byte PASS");
 const unsigned pauses[]={0,1,4,8};unsigned number=0;
 for(unsigned i=0;ok&&i<4;i++)for(unsigned m=0;ok&&m<2;m++)ok=trial(m,pauses[i],++number);
 if(live)while((IO(UART0_IER)&2)||!(IO(UART0_LSR)&0x40))service(); /* Retain live source/code until actual drain. */
 mos_setkbvector(0,0);if(*(volatile uint24_t*)RFC_KB_VECTOR)ok=0;
 if(!clocks_stop())ok=0;
 send(v_cleanup,sizeof v_cleanup);
 if(ok)ok=record("LAT RESTORE PASS: vectors, disabled timer controls/source and null keyboard callback");
 record("LIMIT: write-only reloads not restorable; next timer owner must configure them. Last-buffer receiver check; model oracle checks every wire packet.");
 record(ok?"RC3 LATENCY PASS":"RC3 LATENCY FAIL");mos_fclose(file);return ok?0:1;
}
