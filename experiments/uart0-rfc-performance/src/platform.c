/* PRT1 only: no timer interrupt, vector change or keyboard hook. */
#include <ez80f92.h>
#include "platform.h"
const uint8_t *pf_source;
uint24_t pf_length;
volatile uint8_t pf_done;
volatile uint24_t pf_callbacks;
uint32_t pf_max_poll_gap;
static uint8_t old_ctl,old_iss,running;
static uint16_t previous;
static uint32_t elapsed;
int pf_clock_start(void){
 old_ctl=IO(TMR1_CTL);
 if(old_ctl&0x41)return 0; /* enabled or IRQ-enabled: another owner */
 old_iss=IO(TMR_ISS);IO(TMR1_CTL)=0;
 IO(TMR_ISS)=old_iss&0xf3; /* change only timer1's two source bits */
 if((IO(TMR_ISS)&0x0c)!=0){IO(TMR_ISS)=old_iss;IO(TMR1_CTL)=old_ctl&0x7e;return 0;}
 IO(TMR1_RR_L)=0;IO(TMR1_RR_H)=0;IO(TMR1_CTL)=0x1f;
 previous=(uint16_t)pf_down();elapsed=pf_max_poll_gap=0;running=1;return 1;
}
int pf_clock_stop(void){
 if(!running)return 1;
 IO(TMR1_CTL)=0;
 IO(TMR_ISS)=(IO(TMR_ISS)&0xf3)|(old_iss&0x0c);
 IO(TMR1_CTL)=old_ctl&0x7e;running=0;
 /* Reloads are write-only; a later owner must configure its own reload. */
 return (IO(TMR_ISS)&0x0c)==(old_iss&0x0c)&&
  (IO(TMR1_CTL)&0x7f)==(old_ctl&0x7e);
}
uint32_t pf_ticks(void){
 uint16_t now=(uint16_t)pf_down(),delta=(uint16_t)(previous-now);
 if(delta>pf_max_poll_gap)pf_max_poll_gap=delta;
 elapsed+=delta;previous=now;return elapsed;
}
void pf_gap_reset(void){pf_ticks();pf_max_poll_gap=0;}
