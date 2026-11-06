# RFC-001 second tranche — RC3 responsiveness, then matched performance

Brandon authorized this work after asking for existing work to be committed in
logical groups and pushed before creating a new experimental branch. Historical
commits: 2c5438e (startup attachment), ba5104f (original RFC fixture/results),
6c36ed3 (consumer coordination). All pushed; both owned repositories were clean.
New branch: `codex/rc3-latency-performance`. No MOS/VDP firmware edits or release.

The goal is to find whether normal receiver pauses cause noticeable input or
timer delays, then measure how much foreground compute remains while sending.
Use unchanged published RC3,100879 bytes/CRC32 B08C80B8/SHA256
`d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
Private experimental use pending the RFC merge. No physical flash/card write.

LAT-001 [x] Record scope, source/ROM identity, build/runtime limits and meaningful
controls before implementation. No permanent CTS stall or additional MOS guards.

LAT-002 [ ] Build a directly runnable C/assembly `test` with identical synchronous
and RFC25 asynchronous packets. Exercise ordinary stock VDP C3 VSync waits of
0/1/4/8 frames before an8KiB upload, using the existing positive/negative receiver
byte comparator. Repeat packets during a finite one-second observation window;
verify the final receiver contents outside timing and every model wire packet
independently. One producer/borrow, prearmed flag-only callback; explicit TEMT
before ordinary output or reuse at packet boundary. Record callback/RX/return.

LAT-003 [ ] Reuse inactive PRT1 as a polling72kHz down-counter (wrap0.91s) and
PRT2 as a1ms service interrupt. No high-rate wrap ISR whose ticks can disappear
inside a133ms DI pause. Report maximum timer-service and foreground-observation
gaps; compare serviced VBlank progress. Record overflow assumptions and elapsed
bounds: no single interval >=65536 ticks may be interpreted as accurate. Preserve
original vectors/disabled control/source registers; write-only reload restoration
is unavailable and explicitly documented. Refuse active timers or a preexisting
keyboard callback. Tiny assembly keyboard callback latches events/timestamps;
restore null callback after drain. Measure ISR-delivery-to-foreground latency,
not unobservable physical key-to-ISR latency. No keys means NOT TESTED.

LAT-004 [ ] Compile the fixture and source/host oracles through Pi serial FIFO;
use existing pinned AgonDev library/toolchain.600s whole job,180s/child, serial,
80C/512MiB stop, retain logs/source hashes/map and owned teardown/release. No
heavy test/emulator on Pi. First source/build error stops that attempt; correct
and retain evidence before a fresh bounded build.

LAT-005 [ ] Reserve Oryx only when profiles/finite plan are ready. Two cells,
JIT and interpreter, each300s maximum/60s no wire progress/900s campaign.
Use actual published RC3 and identified actual-firmware receiver; ordinary stock
commands do not make a diagnostic runtime stock VDP. Reuse the unchanged existing
Jukebox PS/2-input shim where its source/binary can be verified; only real PS/2
input injection, no guest memory/vector/timer/result injection. Check keyboard
delivery, timer/foreground progress, final byte comparator plus full host wire,
backend/UART counters and actual CLI return. Stop at first unexpected failure;
retain all evidence, release with fresh idle and notify actual next owner.
Model timings are functional evidence, never physical CPU/latency measurements.

PER-001 [ ] After latency results, extend the same frozen controls to10s windows,
three rotated repeats: no-traffic work calibration; flat-out sync/async with and
without foreground calculation;44,100 payload bytes/s using256-byte payloads.
Fixed immutable payload and same barrier policy on one RC3 image/receiver.
Last-buffer receiver verification plus all model wire packets; distinguish this
from per-packet physical readback. Keep packetization/logging out of timed loops
or charge identical necessary costs. Retained compute uses calibrated work/time,
not syscall duration or a claim that blocked foreground consumes allCPU cycles.

PER-002 [ ] Add Tom's idle-versus-sending tight-assembly-work/VSync comparison
with actual elapsed PRT cross-check and counter-wrap bounds. Keep this separate
from the fixed-time performance window and lost-VSync-under-DI observations.

PKG-002 [ ] Prepare a short current README, source/binary/pin package, sequential
logs and explicit expected duration for Brandon's later Console8 run. No physical
run/deployment implied by source completion; keep receiver identity explicit.
Stop before firmware alteration, broad app migration or new release publication.
