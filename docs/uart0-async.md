# RC3 caller contract — RFC syscall25h

**Breaking from RC2:**25h replaces42h/43h. No implicit queue, BUSY result, null
callback support, cancellation or finish syscall is supplied. The raw RFC returns
an IER-derived A value despite its A=0 comment; callers must not use A as admission
status. The startup fix changes no transport semantics.

Call from one foreground ADL application with actual MB0 and interrupts enabled.
HL is a positive contiguous immutable source; BC is its full24-bit byte length;
DE is a non-null ADL assembly callback returning with RET. Do not submit again
while another source is borrowed. No callback/source may be freed on a timeout.

Arm the completion flag before invoking RST.LIL08h with A=25h. The UART0 ISR
fills at most16 bytes with OTIRX after checking CTS. WAIT_CTS spins under DI;
normal receiver backpressure can delay RX, keyboard, VBlank and timer service.
There is no bounded-latency or stuck-receiver recovery promise.

The callback runs under DI after the last source byte is copied into the FIFO.
Primary AF/BC/DE/HL are saved by MOS; preserve IX/IY/alternate registers and MB
if used. Use a tiny flag-store assembly leaf; no MOS, C runtime, wait, VDU,
allocation or recursive submission. A generic C function needs a separately
correct register/stack bridge; this example does not pretend otherwise.

After observed callback, source RAM may be reused. Poll UART0 LSR bit6 (TEMT)
before ordinary VDU/query output, application exit, or the conservative next
packet boundary used by our example. TEMT does not prove the VDP executed a
command: use its normal ordered reply/fence where required. Finish receiver
ownership before freeing command inputs or changing modes/routes.

Ordinary RST10/RST18 keep synchronous behavior. Applications that never issue
25h keep the established output path. Unsupported caller contexts and zero,
null or overlapping submissions are outside the RFC's valid-caller contract.

Pinned RFC:ffab9c9c84a31535d1ec976b7e6f23b2579ecb80, PR2.
Our startup correction is PR3; unpatched RFC still erases45 default vectors.
The original RC1/RC2 contract is retained under docs/archive for reference.
