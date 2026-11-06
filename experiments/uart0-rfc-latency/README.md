# Unchanged RC3 UART responsiveness fixture

This experiment compares ordinary synchronous output against Tom Morton's
RFC25 background sender in our published startup-fixed RC3. No firmware is
changed. The code is original C/assembly using existing AgonDev and ordinary
stock buffered VDP commands. Private testing pending the upstream RFC merge.

`test` runs eight cases without switches: sync/async with0/1/4/8 ordinary C3
VSync waits before an8KiB upload, repeated over one second, then checking all
bytes of the final receiver buffer. Model-side analysis must additionally
verify every whole packet on the wire. It is not per-packet physical readback.

A polling72kHz PRT1 measures elapsed time without relying on serviced interrupts.
A separate nominal1ms PRT2 interrupt records service gaps. One16-bit clock wrap
is0.91s: individual unobserved intervals must be shorter; external model bounds
and later physical duration checks matter. Counts during an unbounded stall
are not reliable. The program refuses active timers, preserves disabled controls,
sources and interrupt vectors, and documents that write-only reloads cannot
be restored. The next owner must configure its own timer reloads.

The keyboard callback latches events in interrupt context, so brief taps are not
lost by foreground key polling. Its age measures MOS-callback delivery to
foreground observation, not physical key latency. `keys=0` means keyboard was
NOT TESTED, not success. It refuses an existing keyboard callback and restores
null afterward. No output/syscalls or submission from callbacks.

Source and callback remain resident until release, then explicit TEMT before
ordinary output or the next packet. Source release, UART-empty and receiver
execution remain distinct. No permanent CTS blockage is requested. If a test
stalls, report the last progress line; reset may be required. Allow about two
minutes. Sequential Rnnnn.log/next.txt records avoid clock-based filenames.

`prepare.py` freezes sources and exact published RC3 ROM/map identity. Build the
generated fixture with the existing toolchain under Pi FIFO; execute only under
the Oryx emulator FIFO or a separately selected manual Console8 run. Model
measurements validate instrumentation and progress, not physical timing/CPU gains.
This experiment does not authorize SD writes or hardware flashing.

The first campaign found16 modeled receive overruns in interpreter despite guest
PASS, while JIT reported none. See docs/tasks/RFC-001/latency-findings.md. Guest
PASS certifies its transfer/restoration checks, not complete keyboard retention
or acceptable latency. Physical applicability has not been established.
