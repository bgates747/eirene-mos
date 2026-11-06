# KBD-001: small correction candidate ready for target checks

Tom's proposal keeps keyboard events while an application is calculating or
drawing. An application can poll for complete ordered events later, without
installing its own keyboard interrupt callback. This complements background
UART sending: the main loop can work and collect input when ready. It needs an
aware caller of the new62h syscall; existing getkey/state-polling apps keep their
old behavior. No VDP modification is needed.

The idea is practical and the implementation is already small. Retain the
31-event FIFO, four-byte records and drop-new-on-full policy. Do not add a new
input framework, overflow-status ABI, queue ownership stack or legacy-getkey
replacement merely to finish this proposal.31 events include presses, releases
and repeats, not31 complete press/release pairs. It cannot recover events whose
UART packet never reaches MOS, including while an ISR blocks reception.

## Exact review and changes

[Upstream PR4](https://github.com/AgonPlatform/eirene-mos/pull/4), head
241ffbaee4bc7e3f814124b59e0b8c07207a9409, base
3a7259c58bfa6f34f58afe24087f418cef0148e0. Empty body/comments/reviews at review.
The base includes the merged startup correction from PR3, but not the separate
async-UART RFC. Existing RC3 is not replaced by this keyboard-only composition.

Candidate source commit9ccdf45 on bgates747/eirene-mos branch
codex/keyboard-event-buffer. The exact three-file correction is
[proposed-fix.diff](proposed-fix.diff).

- kbuf_remove copies and advances a valid event but returnsZ when the read index
  wraps31->0. Both polling interfaces say empty; the keydown waiter can discard
  that copied keydown and continue waiting. INC A after storing index0..31 gives
  values1..32, guaranteesNZ and replaces OR A without adding a byte.
- kbuf_clear unconditionally enables interrupts. Save incoming IFF2, clear both
  indices with DI, restore its state and preserve AF/HL across the call. This
  also avoids clobbering registers just restored in the assembly app-return
  path. No queue lock/reentrancy redesign is required.
- Include stdbool.h in the new header and correct misc.asm's unused external
  declaration to _kbuf_clear. The original full MOS build succeeds: the symbol
  declaration is cleanup, not a demonstrated link failure. mos.c already got
  bool indirectly from defines.h; no broken full-build claim is made.

Single ISR producer/single foreground consumer is appropriate. Event bytes are
copied before publishing the write index and before releasing the read slot.
The full-buffer attempted write is to the reserved, unpublished slot, so it does
not overwrite an already queued record. Existing keyboard callbacks and normal
keymap/sysvar/reset processing remain on their original path after queueing.
Consumers need a writable four-byte DEU pointer; there is no new implicit
MBASE conversion. No concurrent second consumer or blocking wait with DI.

## Build and linked-code evidence

Compiler256: exact base, unmodified PR and candidate all build using the same
retained AgonDev toolchain/flags. Existing upstream warnings remain in the logs;
the new native fixtures build with warnings as errors. No compiler migration.

| Matched image | Firmware bytes | BSS bytes |
| --- | ---: | ---: |
| Exact PR base |100634|2087|
| Tom's original proposal |100823|2217|
| Corrected proposal |100836|2217|

Tom's complete integration adds189 firmware bytes and130RAM bytes. Our source
corrections add13 firmware bytes and no RAM: total202 firmware bytes over base.
The ring object alone is154bytes text before,167after, plus130BSS in both.
Source diffs, object hashes and final-image hashes are distinct measurements.
Exact image/fixture/map pins: evidence/build-summary.json.

The actual linked dequeue tail is checked for all32 starting indices. Original
reports a copied event empty for index31; corrected tail reports success for all
32. These are bounded instruction-property checks, not an executed target or
full CPU/UART simulation. The existing linked startup verifier passes all three
MOS images and rejects its six negative mutations per image. Initial parser
attempts could not find assignment/local ELF symbols in the link map; resolving
those from the unchanged object symbol table allowed the actual verifier to run.
No firmware change was made to accommodate a verifier.

Matched kcheck fixtures link the actual selected keyboard_buffer.asm into their
own application RAM. Expected original failure is removal32; corrected checks
cover empty destination unchanged, all fields/order,31-record full/drop-new,
128removals, key-up filtering, clear and incoming IFF both ways. Both binaries
compile; neither has executed. They do not test installed MOS62h dispatch or a
real UART interrupt. Source/instructions: experiments/keyboard-events.

All owned build children stopped and compiler256 released20:20:43UTC with no
successor. No emulator, bench, SD, serial, installed firmware, RC release or
upstream discussion was changed. Target execution and integrated62h checks are
the next qualification step, not an unobserved pass.

## Short feedback draft for Tom

The buffered API looks useful. I found one wrap bug: kbuf_remove returnsZ after
successfully copying the event whose new read index is0, so every32nd dequeue is
reported empty. Replacing the final OR A with INC A fixes that without growing
the function. kbuf_clear should also preserve incoming interrupt state rather
than unconditionally enabling it. Those fixes, plus header/symbol cleanup, add
13bytes to your proposal and no RAM. Matched original/corrected test programs
are compiled; target runs and actual62h keyboard integration are still pending.
