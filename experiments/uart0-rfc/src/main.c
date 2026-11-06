/* RFC-001: valid ADL-only functional caller, not a performance benchmark. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "packets.h"
#include "rom_crc.h"
extern void rfc_submit(void),rfc_callback(void);
extern uint8_t rfc_context(void),rfc_lsr(void),rfc_ier(void);
const uint8_t *rfc_source;
uint24_t rfc_length;
volatile uint8_t rfc_done,rfc_callbacks,rfc_returned,rfc_early;
static volatile uint8_t failed_stage;
static uint8_t packet[67588],checks[960];
static volatile uint8_t *sv;
static uint8_t file;
static unsigned report;
static uint8_t sample(unsigned n){return (uint8_t)(n*157u+7u);}
static void send(const uint8_t *p,unsigned n){mos_puts((const char*)p,n,0);}
static int record(const char *s){
 puts(s);unsigned n=strlen(s);
 return mos_fwrite(file,(char*)s,n)==n&&mos_fwrite(file,"\r\n",2)==2;
}
#include "run_counter.inc"
static int report_open(void){
 unsigned n=first_report();if(!n)return 0;char name[16];
 for(;n<10000;n++){
  snprintf(name,sizeof name,"R%04u.log",n);
  uint8_t f=mos_fopen(name,FA_READ);if(f){mos_fclose(f);continue;}
  file=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);if(!file)return 0;
  if(!save_next_report(n+1)){mos_fclose(file);file=0;return 0;}
  report=n;return 1;
 }return 0;
}
static int vector_ok(unsigned vector,unsigned target){
 volatile uint8_t *p=(volatile uint8_t*)(RFC_IRQ_TABLE+2u*vector);
 return p[0]==0xc3&&p[1]==(target&255)&&p[2]==((target>>8)&255)&&p[3]==((target>>16)&255);
}
static int vectors_ok(void){
 return vector_ok(0x18,RFC_UART_ISR)&&vector_ok(0x32,RFC_VBLANK_ISR)&&vector_ok(0x1c,RFC_I2C_ISR);
}
/* This clock cannot bound a CTS spin under DI. Host/human provides that bound. */
static int gp(const uint8_t *p,unsigned n,uint8_t expected){
 uint32_t start=getsysvar_time();sv[sysvar_gp]=0xfe;send(p,n);
 while(sv[sysvar_gp]!=expected)
  if((uint32_t)(getsysvar_time()-start)>1200)return 0;
 return 1;
}
static int idle(void){
 uint32_t start=getsysvar_time();
 while(!(rfc_lsr()&0x40))if((uint32_t)(getsysvar_time()-start)>1200)return 0;
 return !(rfc_ier()&2);
}
/* Positive nonzero source only. Keep storage/code resident on uncertain drain. */
static int transfer(unsigned bytes,int check_rx){
 if(!bytes||bytes>sizeof packet||!idle()||rfc_context())return 0;
 uint8_t before=rfc_callbacks;uint32_t start=getsysvar_time();int expired=0,early_rx=0;
 rfc_source=packet;rfc_length=bytes;rfc_done=0;rfc_returned=0;rfc_early=0;
 rfc_submit();
 while(!rfc_done){
  if(sv[sysvar_gp]==0x51)early_rx=1;
  if((uint32_t)(getsysvar_time()-start)>1200){expired=1;failed_stage=1;}
 }
 /* Prove the source is reusable at release, before requiring TEMT. */
 memset(packet,0xee,bytes);
 while(!(rfc_lsr()&0x40))
  if((uint32_t)(getsysvar_time()-start)>1200){expired=1;failed_stage=2;}
 return !expired&&rfc_callbacks==(uint8_t)(before+1)&&!(rfc_ier()&2)&&(!check_rx||early_rx);
}
static void clear_target(void){const uint8_t p[]={23,0,160,240,106,2};send(p,sizeof p);}
static void write_header(unsigned n){
 const uint8_t p[]={23,0,160,240,106,0,(uint8_t)n,(uint8_t)(n>>8)};send(p,sizeof p);
}
static int verify(unsigned bytes){
 send(v_reset_flag,sizeof v_reset_flag);
 for(unsigned base=0;base<bytes;base+=64){
  unsigned count=bytes-base;if(count>64)count=64;
  for(unsigned i=0;i<count;i++){
   unsigned at=base+i,ref=at&255;
   const uint8_t c[]={23,0,160,241,106,6,0x23,240,106,(uint8_t)at,(uint8_t)(at>>8),244,106,(uint8_t)ref,0};
   memcpy(checks+15*i,c,sizeof c);
  }
  send(checks,count*15);
  if(!gp(v_reply,sizeof v_reply,0))return 0;
  if(bytes>=8192&&((base+count)&16383)==0&&!record("Receiver byte verification: 16 KiB complete"))return 0;
 }
 return 1;
}
static int boundary(unsigned n,unsigned number){
 char line[96];snprintf(line,sizeof line,"Case %u/9: %u-byte borrowed source; release, reuse, receiver check...",number,n);
 if(!record(line)||!idle())return 0;
 uint8_t marker[]={23,0,128,(uint8_t)(0x80+number)};
 if(!gp(marker,sizeof marker,marker[3]))return 0;
 clear_target();write_header(n);
 for(unsigned i=0;i<n;i++)packet[i]=sample(i);
 if(!transfer(n,0)||!verify(n))return 0;
 snprintf(line,sizeof line,"CASE %u PASS payload=%u callbacks=%u early_callback=%u",number,n,rfc_callbacks,rfc_early);
 return record(line);
}
static int large_case(void){
 if(!record("Case 9/9: 67588-byte source, 65536 payload bytes; concurrent RX, then exact byte checks...")||!idle())return 0;
 const uint8_t marker[]={23,0,128,0x89};if(!gp(marker,sizeof marker,0x89))return 0;
 clear_target();memcpy(packet,(const uint8_t[]){23,0,128,0x51},4);
 for(unsigned block=0;block<256;block++){
  uint8_t *p=packet+4+264*block;
  memcpy(p,(const uint8_t[]){23,0,160,240,106,0,0,1},8);
  for(unsigned i=0;i<256;i++)p[8+i]=sample(i);
 }
 sv[sysvar_gp]=0xfe;
 if(!transfer(sizeof packet,1)||sv[sysvar_gp]!=0x51||!verify(65536u))return 0;
 return record("CASE 9 PASS payload=65536 source=67588 RX-before-release=1 source-reused=1");
}
int main(void){
 /* Refuse foreign ROM before issuing25h, touching vector state or using receiver buffers. */
 if(installed_crc(RFC_MOS_BYTES)!=RFC_MOS_CRC){puts("RC3 REFUSED: wrong MOS image; no async submission.");return 1;}
 if(rfc_context()||!vectors_ok()){puts("RC3 REFUSED: required IRQ vectors or ADL/MBASE0/EI context missing.");return 1;}
 putch(12);puts("UART0 RFC TRANSFER CHECK\nAllow about two minutes. If longer, something is wrong.\nReport the last progress line. A stall is FAIL; reset may be required.\n");
 sv=mos_sysvars();if(!report_open()){puts("RC3 FAIL: cannot create sequential report.");return 1;}
 int ok=record("RC3 build=" RFC_BUILD " MOS=matched-RC3 syscall=25h; functional only")&&record("Startup-corrected RC3; required active vectors checked.");
 if(ok)ok=idle();
 if(ok){send(v_setup,sizeof v_setup);ok=gp(v_mismatch_probe,sizeof v_mismatch_probe,1)&&gp(v_match_probe,sizeof v_match_probe,0);}
 if(ok)ok=record("Receiver comparator deliberately wrong byte FAIL / correct byte PASS.");
 const unsigned sizes[]={1,15,16,17,255,256,257,1024};
 for(unsigned i=0;ok&&i<8;i++)ok=boundary(sizes[i],i+1);
 if(ok)ok=large_case();
 if(ok)ok=vectors_ok()&&rfc_callbacks==9&&idle();
 if(ok){
  uint8_t m[]={23,0,128,0x6d};ok=gp(m,sizeof m,0x6d);
  if(ok)ok=record("Ordinary MOS output/query and required IRQ vectors after async PASS");
 }
 send(v_cleanup,sizeof v_cleanup);
 char line[80];snprintf(line,sizeof line,"REPORT R%04u callbacks=%u expected=9 failed_stage=%u",report,rfc_callbacks,failed_stage);
 ok=record(line)&&ok;record(ok?"RC3 TRANSFER PASS":"RC3 TRANSFER FAIL");mos_fclose(file);
 return ok?0:1;
}
