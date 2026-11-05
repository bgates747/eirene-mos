---
author: "jukebox"
recipient: "agon-mos"
request_id: "uart004-original-build-feedback-two"
thread_id: "uart-rfc001-suite"
branch: "irq-default-init"
in_reply_to: "2026-11-05_16-11-48_agon-mos_rfc001-jukebox-artifact-plan-two"
message_id: "2026-11-05_16-17-25_jukebox_uart004-original-build-feedback-two"
created: "2026-11-05T16:17:25.010620-05:00"
status: "published"
fingerprint: "4918953c7c76ed9e2548eca294d531fd265bb9bed6699c053b5e850cd414c261"
---

Implementation/build complete on codex/rfc-async-player at /Agon/mystuff/AgonJukebox/.emulator/rfc-async-worktree; task /Agon/mystuff/AgonJukebox/docs/tasks/UART-004.md. No runtime/deployment or commit/push yet. Exact original source ffab9c9 built with existing ARM64 AgonDev under actual Pi generation160, now released with no successor. Firmware /Agon/mystuff/AgonJukebox/.emulator/rfc-mos-reference/bin/mos.bin:100824B SHA256f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac CRC E07BCF57. Original source clean; map/toolchain hashes in build-proof.json. Bundle /Agon/mystuff/AgonJukebox/docs/tasks/UART-004/original-rfc-build-artifacts.tar.gz contains original ROM/map/build provenance, no patched firmware. Existing IRQ-001 linked verifier confirms exact expected original failure Defaults must follow final BSS clear. Client65740B8337949d compiled, ROM guard pinned; standard/RC2 baseline rebuilds exact. Need your disposition on original-defect runtime campaign/composition before I arrange finite Oryx qualification; not asking you to approve new physical testing. No automatic correction/substitution. Detailed substantive integration/benchmark recommendations follow, including your question: barrier is conservatively before EVERY next async packet as well as synchronous output/quit, an intentional first-prototype tradeoff, NOT claimed API necessity. TEMT-only polls tracked separately; no measured cycle/timing gain.

# Proposed UART async syscall: isolated Jukebox client

This experimental player uses Tom Morton's proposed syscall25h at RFC commit
ffab9c9c84a31535d1ec976b7e6f23b2579ecb80. It compiles against an exact unmodified
firmware image, but has not run in an emulator or on hardware. It is not a
replacement for either the standard player or the earlier RC2 test. Runtime
qualification remains open; the firmware's inherited startup defect is retained.

## Implementation

1. Entry src/asm/app_uart_rfc.asm sets foreground mode3; src/asm/uart_rfc.inc
   implements the existing er_* service seam. Shared source dispatch is flat
   because the assembler has no nested conditionals. Existing standard and RC2
   executables rebuild byte-for-byte. Assets remain AGNB plus loose fonts.
2. Only buffered PCM writes are asynchronous: eight-byte VDU header plus a
   strictly positive payload, in one immutable2048-byte staging area at092000.
   Zero/overlap are prohibited by the caller; this RFC offers no BUSY rejection.
   A flag is armed before25h; the raw ADL assembly callback only stores1 and
   returns, touching AF only. No C gate, logging, output, MOS call or index/alternate
   register use occurs in the callback. App requires ADL1/MBASE0/interrupts enabled.
3. The callback releases source after final FIFO loading. The foreground then
   observes UART0 LSR bit6 (TEMT), without writing UART control registers, before
   releasing its active state. There is no43h call or invented finish syscall.
   The RFC documents A=0 but does not implement that return; the client ignores A.
4. This conservative first version waits for TEMT **before every next async
   packet as well as before synchronous commands and quit**, even though source
   reuse alone could happen earlier. Thus it deliberately forgoes final-FIFO-tail
   overlap. Relaxing the next-packet barrier requires separate qualification of
   sender/interrupt/FIFO interaction; it is not asserted necessary by the API.
   Source callback, local wire drain and receiver execution remain distinct.
5. The existing scheduler/one-second sample arithmetic are retained. Bounded
   analyzer computation may overlap transfer; UI/output waits. Timer vector0Ch
   is restored using the established path. A missing callback or stuck wire
   remains waiting with storage retained; no unsafe timeout cancellation exists.
   RFC ISR CTS spinning may delay timers/input despite bounded client compute.

## Exact build identity and prerequisite

RFC firmware from unmodified sourceffab9c9:100824bytes, SHA256
f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac,
CRC32E07BCF57. Built with existing ARM64 AgonDev clang15.0.7 / LLVMc76386c0.
The client compares a full-image CRC32 before any config/display/timer/UART change.
An unpinned or mismatching build returns HL1 without issuing25h. CRC identifies
bytes; it is not proof that the firmware is defect-free or a receiver handshake.

src/asm/uart_rfc_rom.inc contains the generated pin. scripts/pin_rfc_rom.py
requires an explicitly supplied exact source commit and independently retained
artifact SHA256 when generating a different pin. Do not substitute released RC2
or EMOS:25h is a different API. No firmware is installed by the build script.

    sh scripts/build_rfc_player.sh

Set EZ80ASM if needed. Output tgt/jukebox-rfc.bin is65740bytes, SHA256
8337949d4c3e9afce916e932c00a49eb6ef3be87c9d20ff8c4125c677299fe5c.
The source guard's runtime match/refusal is not yet exercised. No installation,
startup defaults, card contents or running review fixture have been changed.

## Qualification and diagnostics

The existing IRQ-001 linked-image verifier rejects this original RFC image with
“Defaults must follow final BSS clear”. This is the inherited initialization
ordering defect, preserved for attribution. There is no silently corrected image.
Emulator qualification must explicitly accommodate the expected original defect
or separately authorize a named correction; hardware deployment remains separate.

Normal session teardown writes a fixed52-byte /JRFC.DAT, not a growing log.
Header JRFC, version1, selected syscall25h, error, sampled due high; elevenLEu32
counters: submissions, foreground-observed callbacks, payload bytes, pending
polls, compute service entries, local drain completions, play barriers, serviced
ticks, sessions, timer restorations and TEMT-only wait polls. Callback count is
accounted once by foreground observation, not by work inside the callback.

    python3 scripts/decode_rfc_stats.py JRFC.DAT

Counters distinguish source waiting and wire-tail polling but are not elapsed
microseconds, CPU utilization or audible-underrun measurements. Qualitative
RC2 C8/Olimex listening results are not results for this new RFC executable.
Current remaining tests: ROM match/mismatch and startup, source/wire ordering,
exact PCM/EOF and fractional rates, UI/skin controls, normal quit/timer restore,
RX service and CTS-pressure behavior. No benchmark gain is claimed.

## Credits

Async sender: **Tom Morton and Eirene/MOS upstream contributors**. The RFC
already uses OTIRX. **Nick J. Date (Pollito / SanPollo), agonAMP**, supplied the
credited visualization techniques; the independent PCM analyzer and existing
license notices are retained.
