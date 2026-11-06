# KBD-001: finish Tom Morton's buffered keyboard-event proposal

Let applications read complete queued key-down/key-up events after doing other
work, rather than losing short taps between foreground checks or installing
their own keyboard callback. Keep Tom's small ring and separate opt-in API;
do not change ordinary MOS input behavior or add a new keyboard framework.

Brandon requested review and help bringing the idea home in this UART chat on
2026-11-06. Proposal: https://github.com/AgonPlatform/eirene-mos/pull/4,
head241ffbaee4bc7e3f814124b59e0b8c07207a9409,
base3a7259c58bfa6f34f58afe24087f418cef0148e0. Body/comments/reviews were empty
at inspection. The base includes the merged interrupt-startup fix (PR3); it
does not include the separate async-UART RFC. No RC3 replacement is selected.

Work is isolated on codex/keyboard-event-buffer. Existing RC3/UART1 branches,
releases, installed firmware and card appliances remain unchanged. Eirene's
existing upstream toolchain is AgonDev; this does not migrate ZDS II MOS.

## Work

KB-001 [x] Pin and review the exact proposal, existing keyboard state/callback
path, syscall ABI, application entry/exit clearing and interrupt conventions.
Retain the donor and source findings before editing implementation.

KB-002 [ ] Build the unmodified proposal under the normal Pi compiler FIFO.
Record any real build failures separately from source findings. Preserve the
same toolchain/flags for the corrected comparison and account for code/RAM cost.

KB-003 [ ] Make minimal corrections: return success when read index wraps to
zero; preserve incoming IFF when clearing; keep the header self-contained and
external symbol spelling consistent. Keep the existing four-byte event,31-event
capacity, drop-new-on-full policy, original sysvar/keymap/callback path and62h
syscall. Do not change legacy getkey/editor semantics or silently expand scope.

KB-004 [ ] Prepare matched original/corrected native self-check fixtures using
the actual keyboard_buffer.asm, not a rewritten ring model. Cover empty output
unchanged, full/drop-new, ordering, more than32 removals, event fields, key-up/
keydown filtering and clear with IFF both enabled/disabled. Compile the exact
code and report checks; target execution remains a separate manual selection.

KB-005 [ ] Document a simple real-keyboard integration check through62h, including
short taps while busy, modifier/up/down ordering, callbacks and old keyboard
state coexisting, queue saturation, normal app exit and a second launch. Clarify
that queueing cannot recover packets lost before MOS receives them, infinite
input bursts, or make legacy foreground state polling buffered automatically.

KB-006 [ ] Retain exact diff, source/binary/map pins, build results and concise
review conclusions. Distinguish compiled checks from executed target evidence.
Return the candidate and the next qualification step to Brandon. No upstream
comment/PR, release/tag, emulator/bench run or SD deployment is selected here.

## Source findings

In kbuf_remove, the read index is incremented and masked with31, then OR A is
used to promise NZ. For31->0, A is zero, so a valid copied event is reported
empty. This affects62h, the C polling wrapper and the keydown wait wrapper.

_kbuf_clear uses unconditional DI/EI, so a call with interrupts disabled enables
them. Its two index writes need atomicity and incoming interrupt state retained.
The same routine is called at ordinary program boundaries, so avoid unrequested
register clobbers in the hand-written execution return path.

The header uses bool without including stdbool.h; current mos.c indirectly
provides it, but the new header is not independently usable. misc.asm declares
kbuf_clear while calling/exporting _kbuf_clear: check the actual assembler/linker
before describing this unused declaration as a build failure.

The ring is single UART-ISR producer/single foreground consumer. Publish the
write index after copying a full event; advance the read index after copying
it out. Full uses one reserved slot:32*4+2=130bytes RAM,31 usable events.
Writing the unpublished reserved slot before rejecting full does not overwrite
a queued event in this producer/consumer arrangement. No queue/lock redesign
is justified by that ordering alone. Existing callbacks still receive the same
packet and the keymap/sysvar path still runs after queueing.

## Finite build/check plan

One Pi compiler, no guest/device/serial/network-service execution;180seconds
per child and600seconds whole tranche,80C thermal stop and512MiB available-RAM
floor. Stop/join only owned children and release promptly; alert any successor.
Retain failed attempts. Native linked fixtures are prepared evidence, not a
keyboard, ISR-race or hardware pass. Physical Console8 remains manual Brandon
work; Extender retains its own EMOS integration and live-bench custody.
