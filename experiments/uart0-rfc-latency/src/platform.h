#ifndef LAT_PLATFORM_H
#define LAT_PLATFORM_H
#include <stdint.h>
#define TICK_HZ 72000UL
extern const uint8_t *tx_source;
extern uint24_t tx_length;
extern volatile uint8_t tx_done,observing,key_pending;
extern volatile uint24_t tx_callbacks,irq_count,irq_max_gap,key_count,key_coalesced;
extern volatile uint24_t irq_last,key_stamp;
void lat_submit(void),lat_keyboard(void),lat_timer_isr(void),lat_reset(void);
uint24_t lat_down(void),lat_key_poll(void);
uint8_t lat_context(void),rom_byte0(void);
int clocks_start(void),clocks_stop(void);
void clocks_run(void),clocks_pause(void);
uint32_t ticks(void);
#endif
