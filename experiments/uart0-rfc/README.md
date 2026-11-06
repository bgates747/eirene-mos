# Original RFC UART0 transfer check

This small application checks that Tom's proposed background sender delivers
correct bytes while releasing the source buffer and continuing receive service.
It deliberately uses the original proposal, not our RC2 or patched firmware.
It is a functional check; it does not measure CPU savings or audio quality.

Run `test` from its own writable directory. It clears the screen, prints the
expected duration and progress, creates collision-free Rnnnn.log plus next.txt,
and returns normally after PASS. No arguments or LOAD/RUN sequence is needed.
A stall is failure, not success: on hardware report the last line and reset;
headless qualification uses an external bound. No automatic flashing occurs.

Exact MOS: ffab9c9c84a31535d1ec976b7e6f23b2579ecb80, CRC32 E07BCF57.
The known inherited vector-default startup defect remains present. The app
checks its actual UART0/VBlank/I2C vectors and ADL/MBASE0/EI context; it never
uses zero default vectors or repairs startup. A foreign ROM is refused before
calling25h. This is not a hardware-ready firmware announcement.

Eight small cases borrow1/15/16/17/255/256/257/1024 payload bytes after an ordered
stock buffered-write header. One large source borrows67588 bytes, including
framing for65536 payload bytes and an early GP reply. The callback is a tiny
assembly flag/counter store. Each source is overwritten immediately at observed
release, before requiring transmitter-empty. Existing stock buffered conditional
commands compare every receiver byte against a reference whose wrong-byte and
right-byte controls are checked first. No custom VDP protocol is introduced.
Only after local drain may ordinary query/output and logs proceed. Caller
storage/code remain resident while any uncertain source or drain is pending.
No null/zero/overlap or classic/Z80 probes belong to this valid-caller tranche.

`prepare.py --out BUILD --mos ORIGINAL_ROM --map ORIGINAL_MAP` freezes sources,
ROM/map pins and active-vector addresses. Build fixture/ with existing AgonDev
under Pi FIFO. `check_wire.py` checks a captured mos-to-vdp.bin independently;
without an argument it runs synthetic positive and deliberate corruption tests.
An oracle self-test is not target execution. Preserve toolchain/source/image
hashes and actual target reports separately. Runtime scheduling and bounds are
in docs/tasks/RFC-001/first-tranche.md; actual emulator processes require Oryx.

Use source files as an ADL single-producer example. They do not invent a working
status return, BUSY protection, finish43h or cancellation for the proposed API.
App callback/packet and receiver lifetimes remain distinct. Existing licenses
and attribution to Tom Morton and MOS/Agon contributors are retained.
