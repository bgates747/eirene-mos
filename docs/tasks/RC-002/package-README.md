# Eirene MOS 3.1.0 UART0 RC2

An aware application can calculate while MOS sends its buffer to the VDP in
the background, using UART interrupts and up to 16-byte OTIRX refills. Normal
startup and synchronous RST18 behavior remain unchanged. Legacy applications
do not silently switch transport.

RC2 is the smaller successor to RC1 in bgates747's fork, based on Tom Morton's
Eirene 3.1.0_beta_1 and supplied asynchronous sender. It is a prerelease, not an
upstream Eirene or stable MOS release. RC1 remains a verified, more guarded
alternative; its tag, binaries and evidence are unchanged. Main is unchanged.

## RC2 versus RC1

The sender has 286 instruction bytes and 9 bytes of state, compared with RC1's
476 and 11. The optional fixed-target C callback gate adds 29 application bytes.
RC2 removes broad context/foreign-owner checks and moves extra callback register
protection into the application. Normal syscall/interrupt register preservation,
positive-length/BUSY/NULL behavior, full 24-bit accounting, partial final blocks,
RX chaining, bounded CTS handling and explicit finish remain.

These caller obligations matter: use foreground ADL1/MBASE0 with interrupts
enabled, normal UART setup and sole ownership. Raw callbacks must preserve
IX/IY/alternate banks if touched; the supplied C gate does that. RC1-only
applications must review their callback convention before using RC2. RC2 does
not return the former CONTEXT3 rejection. Read source/docs/uart0-async.md.

## Source and build identities

Source/tag target: 825eaf77176247f5b5ba2f940ae73fcace34e7e5
Tag: 3.1.0_uart0_rc_2, on codex/uart0-async.
Upstream: 86b694260e3be3b391284ce4aa8ecc758f7f34e9 (3.1.0_beta_1).
MOS: 100950 bytes; CRC32 9E08D539.
MOS SHA256: a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a.

build-info.json pins compiler/assembler/linker/library hashes, generated app
identities and the source commit. Two clean MOS builds produced identical
bytes. Against hardware-tested TRIM Trial1, version.h is the only MOS source
change and main.o the only changed MOS object. The sender and every other
checked object are identical. RC2's new banner and regenerated exact-ROM guards
have been built/verified, but this precise branded image has not had another
physical run. The included raw hardware reports describe the implementation
before that branding change; their ROM CRC is D5CC99AE, not RC2's CRC.

## What is included

- source/: full frozen MOS source, original notices and historical task evidence.
- fixture/: complete no-argument regression test source, generated packet data
  and exact-ROM identity header; test.bin/checks.bin are ready to run.
- example/: complete original C worked example, ABI bridge, fixed-target C
  callback gate and Makefile; example.bin is ready to run.
- benchmarks/stock, benchmarks/rc1, benchmarks/rc2: complete sources/Makefiles
  for the three matched PERF2 apps, useful as recipes for PRT timing, receiver
  comparison, pacing and useful-work measurement. Ready stock.bin, rc1.bin and
  rc2.bin accompany cases.json and source/config manifests.
- mos-rc2.bin/map: release candidate and map. mos-rc1.bin and mos-stock.bin:
  exact published RC1 and official MOS 3.0.2 comparison/restoration images.
- evidence/: returned Console8 reports, validated analysis and explanation.
- licenses/: retained licenses/credits. SHA256SUMS covers every packaged file.

No VDP firmware or toolchain binaries are included. The sender needs no private
VDP protocol or VDP modification. Use stock Bistromathics VDP 2.16.0 for matching
the documented physical comparison.

## Install and run the short example

Copy this directory to /test/mos-uart0 on your SD. Preserve any earlier results
before replacing an appliance. From that directory use the normal installed
flash MOSlet, retaining its usual checks:

```
flash mos mos-rc2.bin
```

Let the updater finish and reboot normally. Confirm:
`Agon Eirene UART0 MOS Version 3.1.0 RC 2`.
Return to /test/mos-uart0 and type:

```
example
```

Require RC2 EXAMPLE PASS and the normal prompt. It submits one static source,
calculates while waiting for callback/source release, finishes the UART, then
prints its work count/checksum. It creates no report. No LOAD, RUN or switches
are required. The source is intended to be copied/adapted as an application
recipe, not treated as a reentrant or ISR-safe general library.

## Use the C recipe in your application

Start from example/src/main.c and its uart0_async C/assembly bridge. Include
callback_gate.src and callback_gate.inc for a C callback. The callback target
must have external linkage so the fixed-target gate can call it. Give each
callback its own gate; do not overwrite a shared callback slot when submit
might return BUSY. The include explicitly selects ADL1.

C-001 [ ] Prepare a contiguous source and arm your completion flag before submitting.
C-002 [ ] Call u0_submit(source, length, callback_gate). On BUSY/INVALID no new source
   was accepted. Only one borrowed buffer may be outstanding; there is no queue.
C-003 [ ] Keep accepted source bytes immutable and callback/source storage alive.
   Do useful work while awaiting the flag. The callback runs DI on MOS's UART
   interrupt stack: only post flags/counters and return. No MOS calls, output,
   SD access, allocation, waiting, EI or nested submission there.
C-004 [ ] Source completion means bytes entered the FIFO, not that they left the UART
   or that the VDP executed them. Poll u0_finish in foreground, doing work while
   BUSY, before normal output, freeing storage, changing handlers or returning.
   Use a VDP acknowledgement/fence when receiver execution matters.

There is no implicit crash/exit cleanup. A timeout does not make it safe to
free an accepted source. The scheduling interrupt must not become a competing
UART writer. NULL callbacks are supported; finish gives a conservative lifetime
check. MOS still owns and services its receive state machine.

## Run the regression and benchmarks

With RC2 installed, type `test` twice. Require RC2 PASS and the normal prompt
both times. It clears the screen, checks boundary lengths, BUSY/NULL/zero-length,
callback/source reuse, concurrent RX, ordinary output before/after opt-in and
all 8192 payload bytes. Removed context rejection is deliberately not tested.
Allow two minutes per app; a stall or FAIL is failure. Keep its report and last
progress line. Rnnnn.log, next.txt and runs.log use sequential numbering, not
the Agon's unreliable clock. Preserve earlier logs/counters when repeating.

For an apples-to-apples comparison, keep the same stock VDP and use:

| Installed MOS | Command |
| --- | --- |
| `flash mos mos-stock.bin` | `stock` |
| `flash mos mos-rc1.bin` | `rc1` |
| `flash mos mos-rc2.bin` | `rc2` |

After every flash, reboot and return to the application directory. Each app
has an exact-ROM guard and takes no arguments. Require PERF2 PASS. Each runs
bulk-only, paced-plus-calculation and bulk-plus-calculation, three rotated
8192-byte repeats per scenario, with a full receiver byte comparison. Common
compiled C measurement/timer objects are identical; callback-gate overhead is
included in RC2. Run all three apps to obtain a complete matched new data set.
The pre-branding raw evidence is retained separately, not mixed into new logs.

## Read the metrics

The paced case targets 44,100 payload bytes/s. Bulk runs send as fast as possible.
One useful-work step is one identical xorshift calculation, with checked final
state. PRT ticks are 1,152,000/s; the independent wall timer is 72,000/s. Each
run includes a no-traffic calibration, allowing:

```
compute remaining (%) = work rate during sending / no-traffic work rate * 100
sending cost (%) = 100 - compute remaining
```

This is foreground calculation capacity, including time lost waiting in
blocking calls, not direct exclusive CPU-cycle profiling. Payload throughput
excludes command headers; wire throughput includes them. Callback completion,
wire drain and VDP execution are distinct events; do not substitute one timing
for another. The bulk work count conservatively discards its final work unit.

## Hardware evidence and limits

Matched Console8 reports R0054–R0059 passed all 245760 payload bytes, all 27
performance trials and three functional invocations, with correct image/app
identities, checksums, callback counts, clocks and no missed pacing deadlines.
Under the agreed stock-VDP protocol, the smaller implementation retained 86.0%
of no-traffic calculation capacity when sending flat out and completed 64.6%
more paced foreground work than stock MOS. RC1 retained 85.5% and gained 64.0%,
respectively. Bulk payload throughput was about106.2kB/s across the comparison.
The meaningful result is preserved performance with less code; tiny differences
in three short samples do not establish a sustained speedup.

VDP identity, example and cold-boot checks are based on the Author's completion
report; they were not independently fingerprinted/logged. New RC2 branding is
build-only qualified as described above. Other boards, EMOS fit/compatibility,
indefinite running and real application/audio deadlines are not claimed.

## Build and restore

Eirene uses AgonDev, its existing LLVM/Clang toolchain; this does not migrate the
separate original ZDS II MOS. With the compiler and matching Agon libraries
identified in build-info.json:

```
make -C source AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
make -C fixture AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
make -C example AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
make -C benchmarks/stock AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
make -C benchmarks/rc1 AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
make -C benchmarks/rc2 AGONDEV_TOOLCHAIN=/absolute/path/to/agondev
```

Each generated app source already contains the identity/configuration matching
the included firmware. Rebuilding MOS with different tools may change its ROM
CRC; regenerate the app guards if so. Use serial make for the inherited MOS
Makefile's output-directory ordering. No HEX conversion is required. Output
files are under each directory's bin/. Compiler warnings in the firmware are
inherited; the generated apps build with -Werror.

Restore normally with `flash mos mos-stock.bin`, rebooting as prompted. If MOS
cannot boot, use https://github.com/AgonPlatform/agon-recovery and the correct
board's documented ZDI wiring. The updater/recovery code is unchanged.
Official MOS 3.0.2 source: https://github.com/AgonPlatform/agon-mos/tree/v3.0.2.
Its restoration binary SHA256 is
d564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae.

Credits include Tom Morton, Dean Belfield, Lennart Benschop and the upstream
Agon contributors. Preserve original MOS, FatFS/ChaN, allocator and library
notices in source/ and licenses/. Our additions retain the project's MIT terms.
