# RC3 matched CPU-capacity / throughput fixture — PREPARATION ONLY

This original C/assembly caller compares ordinary synchronous RST18 output with
Tom Morton's RFC25 background sender on the SAME published RC3. It does not
modify MOS, VDP or applications. No target run or card deployment has occurred.
Private experiment pending upstream RFC merge; LAT001's modeled receive-loss
finding and the manual Console8 confirmation remain open.

Run `test` later from its writable appliance directory, without switches. It
clears the screen, prints progress, and makes sequential Rnnnn.log/next.txt files.
Three rotated repeats each measure a10second idle-work calibration, flat-out
sending with no calculation, flat-out sending with calculation, and paced
sending with calculation. Each sending case runs synchronous and async. Allow
about five minutes; more than six minutes is wrong. `smoke` is the same source
with0.2second windows and1repeat: instrumentation only, not full performance.
Neither automatically flashes firmware. A stall is FAIL, never PASS; reset may
be needed because an uncertain live transfer cannot be cancelled safely.

Both arms send byte-identical immutable packets:8192 payload/8454 wire bytes
flat out, or256 payload/270 wire bytes paced at nominal44,100 payload bytes/s.
Headers/reset commands are included in wire-byte counts. No intentional VSync
pause or key injection. The same packet-boundary policy applies: source release
allows another packet, with TEMT only at timed-end, ordinary output, verification
and exit. The source remains immutable throughout, and callbacks are tiny ADL
assembly stores. No C callback assumptions or interpretation of raw A as status.

The fixed window can end during a packet, so final drain is included in actual
elapsed time and observed bytes/s. Pacing uses an exact rational accumulator;
the final whole256byte chunk may exceed the nominal payload budget by up to255
bytes, and observed packet counts/rates are reported. Deadline misses are data,
not silently skipped chunks. Packetization, control and source/drain costs stay
inside the sending interval; setup, SD writes and receiver checks are outside.
Every final receiver buffer is checked exactly, with bad-byte/good-byte controls.
A future model oracle additionally checks every full wire packet. This is not
per-packet physical receiver readback.

Useful work is a counted32bit xorshift step with independently checked final
state. Retained capacity=(credited_work/elapsed)/(idle_credited/idle_elapsed).
One boundary work quantum is conservatively uncredited in each interval.
Foregone capacity includes adapter/polling costs, not just UART ISR cycles.
The no-calculation scenario measures throughput; its zero work is NOT evidence
that UART occupies100percent of the CPU. Overlapping submit/source/drain elapsed
observations are not exclusive CPU-time buckets and must not be summed as such.

Only inactive, IRQ-disabled PRT1 is claimed, selecting divided system clock
and /256 (nominal72kHz). No timer vector/IRQ or keyboard callback is installed;
other timer fields are preserved. Single unobserved intervals must stay below
65536ticks (about0.91s), and source/readback/rate must be qualified on the exact
runtime or hardware before using the results. An external elapsed bound matters.
Write-only reload values cannot be restored; a later owner configures them.
Original7e7d Flexe does not implement TMR_ISS0x92: default zero readback is not
source-selection proof. FX167 correction is a separate unadopted candidate.
This preparation is not adoption of a shared timer provider or physical clock
calibration. Serviced VBlank totals are a cross-observation, not an independent
calibrated wall clock under DI.

`prepare.py --out ... --mos ... --map ...` freezes separate full/short sources
and generated tables against exact RC3d7a51147/B08C80B8. Build serially with
existing pinned AgonDev and original libagon.a, normal Pi compiler FIFO. The
report/packet/work oracle has deliberate corruption controls, which do not
simulate target execution. PER-002's separate tight-assembly/VSync experiment
remains separate. MOS and SDK upstream licenses/credits are retained.
