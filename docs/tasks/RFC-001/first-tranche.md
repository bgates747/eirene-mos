# RFC-001 first implementation tranche

Build a small directly runnable transfer check for Tom's exact proposed MOS.
It will prove byte delivery and source lifetime before performance measurements
or game changes. Smith authorized this tranche and requested existing dirt be
committed/pushed first on 2026-11-05. Those commits are 3be10ba/1c13443 in Eirene
and d43a939 in agon-mos. New branch: codex/rfc001-fixture. No sender variant.

S-001 [x] Create the no-switch C/assembly fixture, exact-ROM/context/active-vector
admission, sequential reports, flag-only callback and explicit source/TEMT/receiver
boundaries. Reuse the existing stock buffered-VDP conditional byte comparator.

S-002 [x] Build under the Pi automatic compiler FIFO using existing ARM64
AgonDev. No toolchain installation. One serial compile, 600s external maximum,
retain errors/provenance/maps; stop owned children only. Avoid physical devices.

S-003 [x] Check generated sources/bridge and host wire oracle, including byte
omission/duplication negatives and exact 67588-byte/24-bit transfer. Report
compiled versus runtime-proven separately. No null/zero/overlap submissions.

S-004 [x] If Oryx becomes available through its FIFO, run finite original-RFC
functional checks in separate owned Flexe profiles (JIT/interpreter), plus a
foreign-RC2-ROM refusal control. 300s/cell,60s no-progress bound,900s total,
stop first unexpected failure. Assert checkout immediately before every process;
only owned termination, raw wire/reports/error counters retained, fresh idle
inspection and immediate next-owner release notification. No GUI or card writes.
If queued, keep source/build work progressing; do not preempt human review.

Original MOS pinned ffab9c9, 100824 bytes/CRC E07BCF57/SHA f2602c03...; inherited
vector-default startup failure remains expected and visible. Check actual
UART0/VBlank/I2C vectors before submit; no missing-default dispatch, startup fix,
firmware patch or silently substituted ROM. This is not deployment approval.
Expected normal cases:1/15/16/17/255/256/257/1024 raw borrowed payload bytes,
then 67588-byte framed source carrying 65536 payload bytes and an early GP reply.
Overwrite source at callback, before TEMT, then compare every stored payload
byte through the existing receiver comparator. One callback/case; valid repeat
invocation and normal query/output/return afterward. Report progress per case
and during large readback. The MOS clock cannot recover a DI/CTS stall; retain
live code/data while an uncertain transfer waits, with host/manual reset bound.

Following tranches (not started here): finite CTS/input latency qualification,
matched sync/async/RC2 CPU and throughput metrics, then application cohorts.
No physical firmware flashing or Console8/Extender bench access in this tranche.

## Current result

Compiled cleanly with -Wall/-Wextra/-Werror using existing ARM64 AgonDev under
Pi FIFO generation 162; released with no successor. Source freeze matches the
built files. App 22445 bytes/SHA256
6d487f59cbb727e5bb6a38059cc4d73be4d3ec408296466dfe803454e7c393ae.
Link BSS ends 0x567B9, below app stack 0xB0000 and MOS IRQ table 0xBC389.
Assembly bridge/callback disassembly retained; callback uses primary AF only.
Offline wire oracle passes positive and omitted/duplicated-byte/missing-return
controls. These are host/build checks, not target transfer results.

Three private Oryx profiles are staged STOPPED, with canonical generated
launchers, correct Flexe names, backend/MOS/runtime pins and private FAT images.
Functional JIT/interpreter will each run test twice to check report numbering and
repeat invocation; foreign RC2 control must refuse before report/async state.
Actual result extraction checks both independent streams and both reports.
Retained diagnostic VDP runtime is identified by its full hashes; using stock
buffered commands does not label that receiver binary stock firmware.

Oryx request 7e8703bb24a9 is queued behind Wolf's human-review generation 312 and
Jukebox request adb522f22a0b. No emulator started or owner interrupted. Runtime
command AFTER checkout and fresh host-idle evidence, from Pi:

```bash
ssh -o BatchMode=yes oryx-linuxlite \
  'python3 /home/smith/Agon/mystuff/eirene-mos/build/rfc001/first001-inputs/tools/run.py /home/smith/Agon/mystuff/eirene-mos/.emulator/rfc001-first001/profiles.json --lease ACTUAL_OWNED_LEASE'
```

Assert ownership through the runner before every process; preserve all results,
stop owned children, obtain fresh idle evidence, release and notify the next
agent immediately. No blind replay after failure. New fixture/profile changes
remain uncommitted pending required human validation; no card/hardware writes.

## Campaign completed

All three selected model cells passed. Both engines completed two invocations;
all 269508 payload bytes and 36 transfers/callbacks passed independent wire and
receiver checks. Wrong-ROM control refused correctly. Checkout 314 was released
with fresh empty-host evidence and actual next-owner Jukebox notification.
See qualification.md/qualification.json and model-reports/ for evidence and
limits. The earlier queued status is historical; no hardware or performance
qualification is implied. Runtime-dependent changes remain uncommitted pending
required human validation.
