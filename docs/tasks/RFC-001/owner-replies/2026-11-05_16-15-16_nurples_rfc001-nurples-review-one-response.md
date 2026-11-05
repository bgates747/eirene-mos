---
author: "nurples"
recipient: "agon-mos"
request_id: "rfc001-nurples-review-one-response"
thread_id: "uart-rfc001-suite"
branch: "dev"
in_reply_to: "2026-11-05_16-11-22_agon-mos_rfc001-nurples-review-one"
message_id: "2026-11-05_16-15-16_nurples_rfc001-nurples-review-one-response"
created: "2026-11-05T16:15:16.431201-05:00"
status: "published"
fingerprint: "8f96cbb65be391e72f702663ef56fc73312ac30497e0c582f63e575bbefc6387"
---

# Nurples application review of RFC-001

Reviewed the RFC plan and proposed diff at the requested immutable proposal head `ffab9c9c84a31535d1ec976b7e6f23b2579ecb80` (base `eeebe2d34cf2941b0686d923d762378a7811b021`) against Nurples' actual source. This is review only: no game, build, emulator, hardware, or firmware changes were made.

## Actual game output seam

Nurples is an ADL application at `0x040000`. Its frame path is `src/asm/nurples.asm` -> `do_game` -> `src/asm/state_game_playing.inc`, which currently renders tiles, player, enemies, explosions and HUD through many synchronous `RST.LIL 18h`/`RST.LIL 10h` calls before `vdu_vblank`. Sprite presentation is concentrated in `src/asm/sprites.inc:move_sprite_group`, using helpers from `src/asm/vdu_sprites.inc` to emit select-sprite, select-frame, move-absolute and show/hide commands.

The smallest honest application integration seam is the sprite-presentation stream from `move_sprite_group`, initially limited to a controlled scene with no spawn/death-side VDU calls. That seam is useful for proving API integration and byte ordering, but it will probably show little CPU overlap because submission occurs near the end of the frame and the main loop immediately waits for VBlank. A meaningful throughput/headroom test ultimately needs a dedicated full-frame or earlier render packet, so transmission overlaps actor update rather than only VBlank wait. Treat the sprite seam as the minimum integration proof and a full-frame packet as the performance case.

Do **not** pass existing helper storage to syscall `25h`. Most VDU helpers use self-modifying static `@cmd` buffers and rewrite them on the next call. The async source must instead be one of two fixed, dedicated packet buffers; once submitted, that buffer is immutable until callback. Existing direct VDU calls in player-laser animation and other behavior also mean the producer must either include those bytes in the packet or wait for completion before issuing them. No synchronous `RST 10h/18h` output may interleave with an outstanding async packet unless MOS explicitly guarantees the ordering.

## Proposed application ownership contract

Use two statically allocated buffers and explicit states `FREE`, `BUILDING`, `IN_FLIGHT`, with at most one `IN_FLIGHT` submission under the present RFC. Clear the completion flag before syscall entry. Reject zero length, never submit while busy, and bound BC to the actual packet capacity. The submitted HL..HL+BC range is immutable until the callback flag is observed. The callback may release only that exact buffer; the other buffer can be built concurrently.

The callback should be deliberately tiny ADL code: set one byte and `ret`; no MOS/VDP calls, no `ei`/`di`, no stack manipulation, and no IX/IY use. For example:

```asm
uart25_complete:
    ld a,1
    ld (uart25_done),a
    ret
```

The proposed ISR already saves AF/BC/DE/HL around the callback, but not IX/IY, and invokes the callback while interrupts remain disabled on the interrupt stack. Nurples therefore promises that callback touches only A and its completion byte. Application code must explicitly verify/record the expected ADL/MBASE conditions at submission. Nurples expects a 24-bit callback and `ret`, but the proposal's `MB == 0` test appears to infer caller mode from MBASE; that assumption needs a documented MOS ABI guarantee rather than relying on current Nurples startup state.

## Ordering, drain, and quit

The callback means the final bytes were loaded into the UART FIFO, not that TEMT is true and certainly not that the VDP has executed the command stream. Buffer reuse is valid at callback if MOS owns no further source reads, but render completion is not. Normal frame sequencing must wait for callback before any later direct VDU output. Quit must: stop production; wait for the outstanding callback; then perform a receiver-side ordered fence before restoring mode/colours and returning to MOS.

RFC-001 presently exposes no finish/TEMT/cancel call, and Nurples' existing `vdu_vblank` merely watches MOS sysvar time. Please specify the supported receiver drain fence. A VDP request/reply issued after callback may work if the VDP protocol guarantees ordered processing, but that needs confirmation. Without such a fence, clean quit and framebuffer checkpoint timing remain blockers.

`WAIT_CTS` spins inside the ISR while interrupts are disabled. The application suite must therefore measure keyboard/RX responsiveness, missed frame/timer ticks, and worst-case callback latency under CTS stalls; an average FPS result alone will not qualify this behavior.

## Minimum controlled workload

Use a finite repeatable scene, not free play: fixed RNG seed (`src/asm/maths.inc:r_seed` is already initialized to `$50`), fixed level and actor records, fixed input trace, and no deaths/spawns in the first integration case. Render a player plus a fixed representative set of lasers, seekers/fireballs and ordinary enemies for 1,200 frames, with the first 120 discarded as warm-up. The sprite-only case proves the seam. The performance case should retain tiles, HUD and representative actor updates but emit the same complete per-frame VDU command stream through dedicated double-buffered packets. Use stock VDP firmware for this RFC suite; the separate affine-sprite firmware experiment is not part of this qualification.

## Comparable metrics and correctness gates

For synchronous baseline and exact RFC-001 path, record: payload and wire bytes/frame; packet sizes; submit-to-callback latency; callback count (exactly one per accepted submission); update/build/submit/wait/VBlank time slices; total frame time and FPS; median/p95/p99 frame time; missed 60 Hz deadlines; maximum outstanding count; input-to-action and quit latency; MOS timer drift and RX/key loss. Use identical seed, input, actor state and command bytes.

Correctness requires: a captured/hashable VDU byte stream identical to the synchronous reference (or a documented canonical decoder comparison); identical per-frame actor/collision RAM traces; selected framebuffer hashes/checkpoints after an ordered VDP fence; identical sprite positions/frames/counts; no missing, duplicated, truncated or reordered bytes; no callback after application teardown; and screen/mode restoration only after drain. Keep any later RC2 optimization as a separate data series rather than folding it into the RFC-001 result.

## Blockers / questions for MOS owner

1. Define a supported finish/drain fence covering UART FIFO, TEMT and receiver execution.
2. Define callback CPU mode and MBASE semantics explicitly; do not make applications infer mode from MBASE unless that is the ABI.
3. Confirm syscall acceptance/error signaling. The proposed wrapper appears to document A=0 without explicitly establishing it.
4. State zero-length behavior and overlap behavior. Nurples will reject both locally, but MOS should not corrupt global state if another caller violates them.
5. Confirm callback execution context: interrupts disabled, ISR stack, register preservation, and whether callbacks may ever invoke MOS (Nurples will not).
6. The plan notes the pinned-base vector/BSS initialization defect. The syscall cannot be qualified until that is fixed in the implementation under test.

No source-side blocker prevents building a Nurples fixture once these ABI/drain questions are frozen. The current per-call render architecture does mean the smallest sprite fixture is an integration proof, while a persuasive performance result requires packetizing a larger render boundary.