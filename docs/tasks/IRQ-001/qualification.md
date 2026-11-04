# IRQ-001: reproduced and corrected

Eirene was filling its default interrupt-handler table, then immediately erasing
it while clearing global variables. Ordinary startup hid this because MOS later
reinstalls the three handlers it normally uses. Software trying to claim UART1
instead found an empty entry. This is an inherited Eirene startup defect, not an
OTIRX, callback or RC2 trimming defect. The correction moves one existing call
after the clear. It adds no code, data, checks or new feature.

The original released binary reproduces the defect; the correction passes all
selected model regressions. Extender independently observed the failed UART1
admission on physical EMOS, then successful normal boot after the same ordering
correction. The remaining confidence gate is the exact regular Eirene image on
Console8. No upstream notification or release change has been made.

## Change and build evidence

Baseline: upstream Eirene `86b694260e3be3b391284ce4aa8ecc758f7f34e9`, inherited
by published RC2 `825eaf77176247f5b5ba2f940ae73fcace34e7e5`.
Frozen corrected firmware source: `42a96cd397c1b0f8bbd0cb479a004aa36a48956d`.
Branch `codex/irq-default-init` remains separate from main and released tags.
See [the complete firmware diff](fix.diff).

Only `src/init.asm` and `init.o` differ from RC2. Both images are 100950 bytes;
39 image bytes differ in the existing 0x06E2..0x070D instruction window. All other
MOS objects, including the UART sender, match. Two clean builds are identical.
Original CRC32 `9E08D539`; corrected CRC32 `DBE3E21E`. Full hashes, linked symbols
and build attribution are in [build-info.json](build-info.json).

The 192-byte table at 0x0BC386 lies inside BSS 0x0BC30E..0x0BCB3D. The original
places initialization before the final BSS clear. The correction places it
immediately after that clear, before restoring the saved hard-reset flag and
calling main. Startup remains DI; the helper balances its stack/mask saves.
Cold/warm detection, global-data copying, final stack and UART logic are unchanged.
The toolchain remains upstream Eirene's existing AgonDev; no ZDS project was ported.

The actual-linked-image checker rejects released RC2, accepts the correction,
and rejects six negative cases: missing, early and duplicate initialization,
malformed BSS clearing, short table fill and a table extending outside BSS.
See [linked-checks-r02.json](linked-checks-r02.json). This checks emitted bytes,
not merely the order of source labels.

## Runtime regressions

Eight sequential Oryx Flexe cells passed using the retained actual ESP32 VDP
firmware, precise interrupts and both JIT/interpreter engines:

| Check | Original RC2 | Correction |
| --- | --- | --- |
| Cold boot, each engine | 45 zero defaults, 3 installed handlers correct | All 48 correct |
| Warm reset after poisoning table, each engine | Same 45 erased defaults | All 48 reconstructed |
| UART1 expected-default admission predicate | Refuses | Accepts |
| MOS setintvector install/restore, each fixed phase | Not attempted through invalid defaults | 48/48 pairs |
| UART functional fixture twice, each engine | Existing frozen control | All four invocations pass |
| C callback example, each engine | Existing frozen control | Both pass |
| Complete PERF2, each engine | Existing frozen control | All 18 trials pass |

Eight startup reports contain 384 slot observations. Fixed-image checks perform
192 install/restore pairs through MOS's normal API under DI. The negative case
records invalid entries without jumping through them; it does not manufacture
an uncontrolled crash. Warm resets preserve the warmboot marker and poison
only the table immediately before jumping to ROM startup. The observed hardReset
flag changes from 1 to 0, proving both selected paths ran.

UART checks cover boundary lengths, zero-length/BUSY/NULL behavior, callback/source
reuse, receive processing during sending, source release versus wire drain,
ordinary output before/after use and clean return. All 180224 measured payload
bytes compare correctly at the receiver. PERF2's callback counts, xorshift work
checksums, two clocks and pacing deadlines pass. All UART drop/overrun and backend
failed/unhandled/unregistered/unmapped counters are zero. The same compiled PERF2
C/timer objects match the RC2 control. Model timing is not a hardware speed claim.
No new sender optimization or benchmark gain is attributed to this startup fix.

This campaign reads/checks default slots and exercises installation/restoration;
it is not peripheral IRQ stress or keyboard-event injection. The UART1 admission
result is the exact expected-default predicate, not a claim that this regular
MOS fixture owns or opens an Extender connection. The existing UART0 functional
runs exercise real modeled RX/TX IRQs. The physical EMOS result separately proves
that its actual UART1 ownership handshake is restored.

## Independent physical corroboration

Extender's first EMOS image reproduced the admission failure. Restoring the RAM
vector later did not repair the already-failed startup handshake. Its owner then
installed source `16ec1f78c7ead1f38378c5ee9bee4633bcb62c1d` with the initialization
move before that handshake. Normal boot/input/listener returned without a repair
shim. Complete 131072-byte ROM readback matches prepared SHA256
`f62eed7f6bab8c164dcfe5e700132d289d52352f19d955acccbe1cff81b5e893`.
Both failed and corrected installed images were independently read back exactly.
See [the owner's receipt](extender-installation-receipt.json) and
[its installation account](/Agon/mystuff/agon-extender/docs/tasks/EMOS-001/FLASH-R01.md).
This is corroboration from a different integration/board, not a Console8 run of
our exact regular-MOS binary or full EMOS UART qualification. No peer bench
operation was performed or requested by this task.

## Archive and next gate

Full source/build/ELF/symbol/runtime/wire/card/report evidence is retained on both
Pi and Oryx under `build/tm001/irq001-{build001,runtime002}`. A verified archive
`build/tm001/irq001-evidence.tar.gz` has SHA256
`3719475b944cf9bf1841d68b306f8e6e760889ed8c089d0a7793eaf457ddd9ea`.
All 878 regular archive members were compared against their checksum manifest;
Pi/Oryx archive and mirrored-file checks match. [Raw readable reports](model-reports/)
and [the qualification receipt](qualification.json) are tracked in this task silo.
The first partial staging cohort `irq001-runtime001` remains retained: it never
ran because Oryx's shared setup helper lacked the new executable verifier. The
successful cohort used a task-frozen copy of the canonical Pi verifier without
changing shared tools, runtime models or firmware. No runtime cell failed.

Oryx lease generation256 was released with fresh whole-host idle evidence; no
next waiter was present. All emulator profiles are stopped.

`build/tm001/irq001-package001` is a private, checksum-verified before/after
appliance plus complete frozen MOS/test sources, maps and diff. Its manual
[hardware protocol](hardware.txt) requires stock Bistromathics VDP2.16.0 and
normal updater checks. It compares original/fixed cold and warm starts, then
runs the corrected UART fixture twice, example and all PERF2 trials. It does
not modify root startup, deploy to SD, flash hardware or launch a test itself.
All physical actions remain the Author's. Upstream contact, a PR and release
promotion remain deferred pending this evidence review/physical gate.
