#ifndef PF_PLATFORM_H
#define PF_PLATFORM_H
#include <stdint.h>
#define PF_HZ 72000UL
extern const uint8_t *pf_source;
extern uint24_t pf_length;
extern volatile uint8_t pf_done;
extern volatile uint24_t pf_callbacks;
extern uint32_t pf_max_poll_gap;
void pf_submit(void);
uint24_t pf_down(void);
uint8_t pf_context(void),rom_byte0(void);
int pf_clock_start(void),pf_clock_stop(void);
uint32_t pf_ticks(void);
void pf_gap_reset(void);
#endif
