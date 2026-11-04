# IRQ-001: Eirene interrupt defaults must survive startup

Author assigns ownership, correction and strong before/after regression testing.
Write/commit this task before modifying startup. Do not notify upstream or
publish a new release until the evidence is convincing and reviewed. Preserve
all released RC1/RC2 tags/assets and main. Extender retains its own integration,
hardware and source ownership; no access to its bench is selected here.

The reported inherited defect is a call to __init_default_vectors before BSS
clearing, even though its 48*4-byte second-level IRQ jump table lives in BSS.
Main later installs UART0, VBlank and I2C, masking the lost defaults for those
three paths. UART1 and other default slots expose the missing initialization.
Extender's source correction16ec1f78 moves that call after final BSS clearing.
Baseline upstream86b694260e3be3b391284ce4aa8ecc758f7f34e9; released RC2
825eaf77176247f5b5ba2f940ae73fcace34e7e5 (CRC329E08D539).

IRQ-001 [x] Freeze the task and before/after contract on isolated branch
codex/irq-default-init. Keep evidence for the original source and released
binary; use the existing AgonDev toolchain on Oryx. Runtime tests use actual
firmware Flexe through the canonical Oryx lease. No emulator model changes.

IRQ-002 [x] Move only the default-table initialization call after final BSS
clearing, before saved hardReset restoration and main. Preserve startup DI,
reset detection, stack balance, .data setup, all UART logic and table layout.
No new feature, ownership relaxation or defensive framework. Build twice and
attribute source/object/image deltas; sender object must remain unchanged.

IRQ-003 [x] Add a linked-image startup-order verifier with meaningful negative
cases: released RC2 must fail, corrected image pass, absent/early/duplicate
initialization or malformed clearing must not be mistaken for a valid fix.
Use actual symbols/opcodes and BSS/table bounds; retain raw diagnostics.

IRQ-004 [x] Build a no-argument target fixture that reads all48 jump slots after
normal boot, checks the3 installed handlers and45 defaults, and reproduces the
UART1 expected-default admission failure on the unmodified release. The same
measurement logic must check the fixed image. Record exact ROM identity and
slot bytes, not merely successful banner/prompt output. Never execute an
unchecked zero target just to create an uncontrolled crash.

IRQ-005 [x] Exercise both cold boot and preserved-RAM software reset. Deliberately
poison the RAM table only with DI immediately before the fixture's explicit
software reset, proving defaults are reconstructed rather than surviving from
a prior image. Preserve the first report before reset; return cleanly after
the second. On the fixed image, verify installation/restoration through the
existing setintvector API for all48 slots under DI, retaining normal handlers.
Label synthetic tests honestly; do not claim peripheral IRQ stress from reads.

IRQ-006 [x] Run the original and corrected binaries in both Flexe engines under
a finite first-unexpected-failure campaign. Original must reproduce the same
missing-default invariant on cold and warm starts; corrected must pass both,
including table poisoning and vector round trips. Retain expected failures,
source/symbols, wire streams, reports and engine/drop/error counters. Stop only
owned processes and release Oryx promptly with fresh host-idle evidence.

IRQ-007 [x] Rerun matching UART functional/C example and the existing full PERF2
scenarios against the corrected MOS, with regenerated exact-ROM guards. Keep
measurement C/timer objects identical; check every payload byte, callbacks,
normal output/return, source reuse and clock/checksum integrity. Model timing
is not a physical performance claim. Broaden only for a failure/new concern.

IRQ-008 [x] Archive verified results on Pi/Oryx, document what reproduced, why
prior UART0 tests missed it, what is fixed and remaining physical proof. Prepare
a concise Console8 before/after appliance/protocol if model qualification passes;
physical flashing/execution remain Author actions. No upstream notification,
PR or release replacement in this task; propose the next confidence gate from
the evidence rather than claiming unrun tests passed.

Finite campaign: serial Oryx builds plus at most eight model cells (original
startup, fixed startup, fixed UART functional/example, fixed PERF2 xJIT/interp),
each300s maximum with a45s no-progress watchdog and first unexpected failure
stop. One controlled cold/warm pair per startup cell; two UART regression
invocations and one C example per functional cell; nine existing PERF2 trials
per performance cell. No physical target or SD writes are started automatically.

Completed owner work: [qualification and remaining physical gate](qualification.md).
The prepared Console8 procedure is [hardware.txt](hardware.txt); it has not
been deployed or executed on Console8. A real EMOS installation independently
corroborates this mechanism, but is not substituted for that exact-image gate.
No upstream message, PR, release/tag replacement or main-branch merge occurred.
