/* Reuses the earlier PRT ownership recipe, with a slower polling clock. */
#include <agon/mos.h>
#include <ez80f92.h>
#include "platform.h"
const uint8_t *tx_source;
uint24_t tx_length;
volatile uint8_t tx_done,observing,key_pending;
volatile uint24_t tx_callbacks,irq_count,irq_max_gap,key_count,key_coalesced;
volatile uint24_t irq_last,key_stamp;
static void *old1,*old2;
static uint8_t ctl1,ctl2,iss,running;
static uint16_t previous;
static uint32_t elapsed;
int clocks_start(void){
 ctl1=IO(TMR1_CTL);ctl2=IO(TMR2_CTL);
 if((ctl1|ctl2)&1)return 0;
 iss=IO(TMR_ISS);
 old1=mos_setintvector(0x0c,(void*)0);mos_setintvector(0x0c,old1);
 old2=mos_setintvector(0x0e,lat_timer_isr);
 IO(TMR1_CTL)=0;IO(TMR2_CTL)=0;IO(TMR_ISS)=iss&0xc3;
 IO(TMR1_RR_L)=0;IO(TMR1_RR_H)=0;
 IO(TMR2_RR_L)=0x80;IO(TMR2_RR_H)=4; /* 1152 at1.152MHz, approximately1ms */
 IO(TMR1_CTL)=0x1f; /*72kHz, periodic, IRQ disabled; wrap65536/72000s*/
 previous=(uint16_t)lat_down();elapsed=0;running=1;return 1;
}
void clocks_pause(void){IO(TMR2_CTL)=0;observing=0;}
void clocks_run(void){lat_reset();IO(TMR2_CTL)=0x57;observing=1;}
int clocks_stop(void){
 if(!running)return 1;
 clocks_pause();IO(TMR1_CTL)=0;
 void *got1=mos_setintvector(0x0c,old1),*got2=mos_setintvector(0x0e,old2);
 IO(TMR_ISS)=iss;IO(TMR1_CTL)=ctl1&0x7e;IO(TMR2_CTL)=ctl2&0x7e;running=0;
 /* Disabled control/source/vector state restored. Reloads are write-only and
    cannot be restored; future owners must configure their own reloads. */
 return got1==old1&&got2==(void*)lat_timer_isr&&IO(TMR_ISS)==iss&&
  (IO(TMR1_CTL)&0x7f)==(ctl1&0x7e)&&(IO(TMR2_CTL)&0x7f)==(ctl2&0x7e);
}
uint32_t ticks(void){uint16_t now=(uint16_t)lat_down();elapsed+=(uint16_t)(previous-now);previous=now;return elapsed;}
