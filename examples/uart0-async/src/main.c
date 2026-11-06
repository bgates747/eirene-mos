/* Prepared for Brandon. MIT. Tom Morton RFC25 single-buffer recipe. */
#include <agon/mos.h>
#include <stdint.h>
#include <stdio.h>
extern void example_submit(void);
extern uint8_t example_context(void),example_lsr(void);
const uint8_t *example_source;
uint24_t example_length;
volatile uint8_t example_done;
static const uint8_t message[]="RC3 asynchronous message: foreground work overlaps UART0.\r\n";
int main(void){
 if(example_context()){puts("RC3 EXAMPLE REFUSED: require ADL/actualMB0/EI");return 1;}
 putch(12);puts("RC3 RFC25 EXAMPLE: should finish immediately; a stall is failure.");
 while(!(example_lsr()&0x40)){}
 example_source=message;example_length=sizeof message-1;example_done=0;
 example_submit();
 volatile uint32_t work=0;uint32_t checksum=0;
 while(!example_done){work++;checksum=checksum*33u+work;}
 /* Release is not drain. Keep callbacks resident and serialize ordinary output. */
 while(!(example_lsr()&0x40)){}
 printf("RC3 EXAMPLE PASS work=%lu checksum=%lu\n",(unsigned long)work,(unsigned long)checksum);
 return 0;
}
