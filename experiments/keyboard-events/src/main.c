/* SPDX-License-Identifier: MIT
 * Unit fixture links the actual MOS ring assembly into application RAM.
 * It does not replace/inject the installed MOS keyboard handler or use 62h.
 */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "keyboard_buffer.h"
_Static_assert(sizeof(struct keyboard_event_t)==4,"event ABI");
extern uint8_t test_append(const struct keyboard_event_t *);
extern uint8_t test_clear_off(void),test_clear_on(void);
static unsigned checks;
#define CHECK(x) do { ++checks;if(!(x)) {printf("KBD SELFTEST FAIL check=%u line=%u\n",checks,(unsigned)__LINE__);return 1;} } while(0)
static struct keyboard_event_t event(unsigned n) {
    struct keyboard_event_t e={(uint8_t)n,(uint8_t)(n^0x55),(uint8_t)(n+3),(uint8_t)(n&1)};return e;
}
int main(void) {
    struct keyboard_event_t e,out,expected;
    putchar(12);puts("KEYBOARD RING SELFTEST - actual local MOS ring code, not installed MOS62h");
    puts("Finite immediate checks. Expect PASS or a specific FAIL; no key input needed.");
    kbuf_clear();memset(&out,0xa5,sizeof(out));expected=out;
    CHECK(!kbuf_poll_event(&out));CHECK(!memcmp(&out,&expected,4));
    puts("Checking FIFO capacity and drop-new behavior...");
    for(unsigned n=0;n<31;++n) {e=event(n);CHECK(test_append(&e));}
    e=event(200);CHECK(!test_append(&e));
    for(unsigned n=0;n<31;++n) {expected=event(n);CHECK(kbuf_poll_event(&out));CHECK(!memcmp(&out,&expected,4));}
    CHECK(!kbuf_poll_event(&out));
    puts("Checking index wrap (includes removal32), all fields and C boolean return...");
    for(unsigned n=31;n<128;++n) {
        e=event(n);CHECK(test_append(&e));CHECK(kbuf_poll_event(&out));CHECK(!memcmp(&out,&e,4));
    }
    CHECK(!kbuf_poll_event(&out));
    puts("Checking key-up filtering and clear...");
    e=event(2);CHECK(test_append(&e));expected=event(3);CHECK(test_append(&expected));
    kbuf_wait_keydown(&out);CHECK(!memcmp(&out,&expected,4));CHECK(!kbuf_poll_event(&out));
    e=event(5);CHECK(test_append(&e));kbuf_clear();CHECK(!kbuf_poll_event(&out));
    puts("Checking incoming interrupt state...");
    CHECK(test_clear_off()==0);CHECK(test_clear_on()==1);
    printf("KBD SELFTEST PASS checks=%u\n",checks);return 0;
}
