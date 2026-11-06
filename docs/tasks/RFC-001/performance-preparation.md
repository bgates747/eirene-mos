# RFC-001 / PER-001 preparation — unchanged RC3 compute/throughput caller

Brandon's verified overnight direction2026-11-06 continues clearly defined
immediate work and prioritizes MechAgon, then Wolf3D. Original human messages
01a1afea-64aa-7702-b51e-724851c54fcd and01a1afeb-04ce-7263-8ea6-bd889603881c,
turn01a1afea-645b-79f0-a7b9-8790abd9a7cf in pi5 manager were inspected through
its retained original-human-source.json. This prepares the already selected
PER-001 caller; it does not dispose of LAT-005, select hardware, run a new target
cohort, change firmware or publish a release. Use existing experimental branch.

PF-001 [x] Record scope and preserved gates before source work. Exact published
RC3 B08C80B8/d7a51147 remains unchanged. MechAgon parallel VALID investigation
belongs to Extender; Wolf currently owns its hardware suite. Do not acquire
bench or Oryx custody or interrupt either. Send only substantive dependencies.

PF-002 [ ] Prepare `test.bin`, no switches, with3 rotated repeats of: idle-work
calibration; flat-out synchronous and async output without credited calculation;
flat-out paired output with calculation; paired256-byte chunks averaging44,100
payload bytes/s. Full windows10s; separate short `smoke.bin` uses the identical
source with compile-time short windows and1repeat, never relabelled as full data.
Matched immutable wire packets include reset/write headers in both arms. One
producer and borrowed source, prearmed assembly callback. Between packets await
source release only, not TEMT; both arms share that policy. Require TEMT before
normal output, receiver checks and exit. Include actual tail drain in elapsed.

PF-003 [ ] Reuse inactive PRT1 polling72kHz clock, no timer IRQ or keyboard hook.
Restore prior disabled controls/source bits, refuse active timer/foreign ROM or
MBASE/IFF. Readback is not proof of source selection on an unimplemented model:
original7e7d lacksTMR_ISS0x92, FX167 candidate is separate and not adopted here.
Single unobserved interval must be <65536ticks; external duration evidence is
required before physical rates. Reloads are write-only/nonrestorable. No timer
ownership or calibration claim extends to another app/provider by this build.

PF-004 [ ] Independent report/oracle validates counters, packet totals, callback
counts, xorshift work states and nominal pacing, including deliberate bad-state,
missing-case and callback/packet corruption controls. Retained capacity is
(work/time)/(idle_work/idle_time). Foregone capacity includes caller bookkeeping;
it is not exact ISR-cycle accounting. Zero work while blocking is not proof
that UART code occupies100percent of the CPU. Keep submit/release/drain elapsed
observations distinct; don't add overlapping intervals as exclusive CPU buckets.

PF-005 [ ] Freeze full/short sources and generated identity/packet tables against
published RC3. Build serially with pinned existing AgonDev library under actual
Pi FIFO.2binaries,600s whole/180s child,80C/512MiB guard; first error stops attempt,
retain it and correct source before a fresh bounded build. No compiler install.
Retain map/disassembly and source/hash receipts; release immediately and notify
actual successor. MechAgon/Wolf priority requests are not preempted.

PF-006 [ ] Prepare local private package with exact source, binaries, unchanged
MOS and concise expected-duration instructions. Do not write a card or launch
smoke/full guest. Future target selection/qualification remains separate;
LAT001 model receive losses and manual Console8 confirmation remain OPEN.
PER-002's separate tight-assembly/VSync reproduction is not implemented by this
prep. No background watcher or indefinite waiting loop is introduced.
