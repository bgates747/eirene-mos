/* Actual post-boot RAM proof. The negative case never jumps through zeros. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "identity.h"
#include "rom_crc.h"
extern void irq_di(void),irq_ei(void),irq_stub(void),irq_warm_reset(void);
static uint8_t file;static int logging=1;
#include "run_counter.inc"
static int record(const char*s){puts(s);unsigned n=strlen(s);if(mos_fwrite(file,(char*)s,n)!=n||mos_fwrite(file,"\r\n",2)!=2)logging=0;return logging;}
static uint24_t target(unsigned i){volatile uint8_t*p=(volatile uint8_t*)(IRQ_TABLE+4*i);return (uint24_t)p[1]|((uint24_t)p[2]<<8)|((uint24_t)p[3]<<16);}
static unsigned opcode(unsigned i){return *(volatile uint8_t*)(IRQ_TABLE+4*i);}
static int phase_read(void){uint8_t f=mos_fopen("phase.txt",FA_READ);if(!f)return 0;char c=0;mos_fread(f,&c,1);mos_fclose(f);return c=='1';}
static int phase_write(char c){uint8_t f=mos_fopen("phase.txt",FA_WRITE|FA_CREATE_ALWAYS);if(!f)return 0;unsigned n=mos_fwrite(f,&c,1);mos_fclose(f);return n==1;}
static unsigned roundtrips(void){unsigned ok=0;irq_di();for(unsigned i=0;i<48;i++){uint24_t old=target(i);unsigned op=opcode(i);void*p=mos_setintvector(i*2,irq_stub);int good=(uint24_t)p==old&&opcode(i)==0xc3&&target(i)==(uint24_t)irq_stub;void*q=mos_setintvector(i*2,(void(*)(void))old);if(good&&(uint24_t)q==(uint24_t)irq_stub&&opcode(i)==op&&target(i)==old)ok++;}irq_ei();return ok;}
int main(void){
 putch(12);puts("IRQ STARTUP REGRESSION: allow two minutes.\nOne deliberate software reset occurs after the first report.\nA stall is failure; retain the last progress line.");
 uint32_t crc=installed_crc(MOS_BYTES);int fixed=crc==FIX_CRC;if(!fixed&&crc!=BASE_CRC){puts("IRQ UNKNOWN MOS: no table/reset operation performed");return 1;}
 unsigned n=first_report();if(!n||n>=9999)return 1;char name[16];for(;n<9999;n++){snprintf(name,sizeof name,"I%04u.log",n);uint8_t f=mos_fopen(name,FA_READ);if(f){mos_fclose(f);continue;}file=mos_fopen(name,FA_WRITE|FA_CREATE_NEW);break;}if(!file||!save_next_report(n+1))return 1;
 int phase=phase_read(),ok=1;char line[160];unsigned hard=*(volatile uint8_t*)HARD_RESET;
 snprintf(line,sizeof line,"IRQ build=%s case=%s phase=%s CRC32=%08lX hardReset=%u",IRQ_BUILD,fixed?"fixed":"original",phase?"warm-poisoned":"cold",(unsigned long)crc,hard);record(line);if(hard!=(unsigned)!phase)ok=0;
 unsigned bad=0,zero=0,activebad=0;for(unsigned i=0;i<48;i++){unsigned op=opcode(i);uint24_t t=target(i),want=expected[i];int good=op==0xc3&&t==want;if(!good){bad++;if(want!=DEFAULT_IRQ)activebad++;}if(!op&&!t)zero++;snprintf(line,sizeof line,"SLOT %02X opcode=%02X target=%06lX expected=%06lX %s",i*2,op,(unsigned long)t,(unsigned long)want,good?"OK":"BAD");record(line);}
 int uart1=opcode(13)==0xc3&&target(13)==DEFAULT_IRQ;snprintf(line,sizeof line,"SUMMARY slots=48 bad=%u zero=%u active_bad=%u UART1_admission=%s",bad,zero,activebad,uart1?"ACCEPT":"REFUSE");record(line);
 if(fixed){if(bad||!uart1)ok=0;unsigned trips=ok?roundtrips():0;snprintf(line,sizeof line,"VECTOR ROUNDTRIPS %u/48",trips);record(line);if(trips!=48)ok=0;}
 else{if(bad!=45||zero!=45||activebad||uart1)ok=0;record("ORIGINAL DEFECT:45 erased default slots; UART1 admission refused");}
 if(ok&&logging)record(fixed?"IRQ FIX PASS":"IRQ ORIGINAL REPRODUCED");else record("IRQ UNEXPECTED FAIL");mos_fclose(file);if(!ok||!logging)return 1;
 if(!phase){if(!phase_write('1'))return 1;puts("IRQ warm reset: DI, poison192 table bytes, restart now");irq_warm_reset();return 1;}
 if(!phase_write('0'))return 1;puts("IRQ COLD/WARM PAIR COMPLETE");return 0;
}
