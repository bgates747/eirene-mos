# RFC-001: eight-project review and plan changes

All eight owners found a feasible first use for the sender, but none recommends
replacing every ordinary output call blindly. The shared work is persistent
packet ownership, correct ordering and meaningful matched measurements. This
review produced the r02 plan; it has not qualified the proposed firmware or
measured a new application performance gain.

## Received reviews

Each named message is retained verbatim in owner-replies/; reply-index.json
records exact IDs. Source revisions/hashes and detailed caveats remain in those
originals. Delivery receipts are separate from substantive review or acceptance.

| Owner | Substantive reply,2026-11-05 | Adopted minimal cohort |
| --- | --- | --- |
| Nurples | 16-15-16_nurples_rfc001-nurples-review-one-response | move_sprite_group integration proof, then full-frame packets overlapping actor updates |
| Fsim | 16-14-57_fsim-pingo_rfc001-fsim-source-review-two | Fixed airborne Corsair trace; persistent request packets and separately owned receiver frames |
| Wolf | 16-19-58_wolf3dorig_rfc001-wolf-source-return-one | r07 bespoke 24-byte packet, then separate VDPlet 65-wire-byte transaction |
| Jukebox | 16-10-36_jukebox_uart004-rfc-integration-plan-one; 16-17-25_jukebox_uart004-original-build-feedback-two | UART-004 migration is independently authorized and compiled; PCM packet only |
| Extender | 16-12-41_linux-extender_rfc001-extender-source-review-one | EMOS Legacy/UART0; retain existing IRQ/RX/UART1 and appliance lifecycle |
| VDPlet | 16-13-33_vdplet_rfc001-vdplet-source-review-return-one | Existing ordinary-buffer upload plus checked numeric module/RPC lifecycle |
| Rally | 16-15-44_rally_rfc001-rally-source-review-return-one | STANDARD direct-eZ80/stock VDP, complete identical frame packet |
| MechAgon | 16-15-57_mechagon_rfc001-source-review-mechagon-one | RAD-02 mode 149 grid/one tank; bounded persistent 256-byte packet |

## Common threads and dispositions

D-001 [x] Persistent storage is a real application change. Nurples rewrites
self-modifying @cmd helpers; Fsim/Rally/MechAgon/VDPlet have stack packets or
reused header/sample storage. A direct async replacement would outlive those
sources. Adopt a complete persistent packet, single foreground producer and
one outstanding immutable borrow. Two app packet slots may overlap preparation,
without adding a queue to MOS. Prearm TX flags and RX tokens; callback and
receiver reply are independent events which can be observed in either order.

D-002 [x] Keep three completion meanings distinct: last source read, physical
UART empty, selected receiver operation complete. Tiny flag-only assembly
callbacks first, no output/MOS/next-submit in an ISR. Establish actual ADL/MBASE0
and full-width arguments instead of assuming them from assembler directives.
Foreground owns teardown and keeps buffers/callbacks resident until all actual
owners release them. The suite must qualify an explicit ordered receiver fence,
not invent finish43h or equate a callback with completed rendering.

D-003 [x] CTS spinning inside DI is the common responsiveness concern. Test
finite pauses, normal simultaneous RX and input/timer progress with an external
bound. No permanent-stall soak is required. Serviced PRT/VBlank ticks can miss
real time during DI; retain independent observer evidence and timer ownership,
wrap/saturation and restoration. Do not steal Jukebox's pacing timer or turn
shared elapsed slices into additive exclusive CPU-time percentages.

D-004 [x] Packetization is a confounder. Include fragmented synchronous as a
reference, but compare packetized synchronous against byte-identical packetized
async on the SAME RFC image/VDP. Retain pinned base sync to detect base/compiler
changes; keep old RC2 separate. Count packet build/copy/barrier/HUD costs and
fixed useful work once in whole-frame totals. Retained foreground-work capacity
is a calibrated proxy; blocked foreground is not proof of 100% UART CPU execution.

D-005 [x] Prefer a small valid ADL case over new MOS machinery. Invalid zero,
null callback and overlap behavior remain isolated ABI questions; callers avoid
them. Nurples's suggestion of additional MOS rejection protection is not adopted
as an automatic requirement: first define the minimal valid contract and prove
normal use. No resident metrics, queue, cancellation service, new receiver hook
or generic runtime redesign is justified by these reviews. Measure real linked
ROM/BSS and app RAM, especially for EMOS; the proposed sender declares 11 BSS bytes.

D-006 [x] Keep startup evidence and firmware identity explicit. The pinned base
has the already known vector-initialization-before-BSS ordering. Jukebox built
exact original ffab9c9 with no patch, and its linked verifier reproduced that
failure. UART independently verified 100824 bytes, CRC E07BCF57 and SHA256
f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac.
See reference/original-rom.json. Do not conflate it with RC2 or call it ready for
hardware. A future corrected-startup cohort must apply the same fix to both
comparison arms and retain original failure evidence. No new correction is
implemented by this planning turn.

## App-specific adjustments and honest limits

Nurples source at 0x40000: do_game/state_game_playing emits tile/player/enemy/HUD
output through multiple ordinary calls. The late move_sprite_group seam mainly
precedes VBlank waiting; it is integration proof, not the persuasive headroom
case. Adopt its fixed seed 0x50, initially no spawn/death, representative actors,
1200 frames/120 warmup and eventual complete frame packet. Stock VDP; no affine
sprite project dependency. Requested receiver-fence definition remains owner
ABI work, not presumed proven by vdu_vblank watching a MOS clock.

Fsim source HEAD 80590249, agon/corsair-flight/src/main.cpp:bytes and
utilities/pingo-vdplet-flight/backend.inc are the actual seams. Local 37-byte
requests/11-byte pose headers cannot escape their call. Its native_frame remains
owned until PREPARE/RENDER/present replies, even after TX storage release. Small
live packets may improve service gaps rather than FPS; asset upload is separate.
Preserve dropped 30 Hz-step accounting, fixed airborne work and paused contact
work. Do not slip a controller-API migration into the transport comparison.

Wolf r07 source copies/manifests distinguish the bespoke 24-byte pose17+render7
packet from the VDPlet 65-wire-byte clear/write/payload/consolidate/RUN transaction.
The latter's 28-byte scene payload is not the whole stream. Adopt its canonical
enemy-free E1L1 tile 34,36, fixed assets and 600 pose trace. Earlier A timings omitted
INIT_LEVEL/map binding and are invalid controls; do not reuse that apparent gain.
Native render DONE is separate from C3/presentation and optical output. Its
current four-way emulator investigation retains its own human scope.

Jukebox UART-004 is isolated at
`/Agon/mystuff/AgonJukebox/.emulator/rfc-async-worktree`, task
`/Agon/mystuff/AgonJukebox/docs/tasks/UART-004.md`. Only ps_read_sample PCM packet
output changes; UI stays synchronous, timer0c ownership remains. It has compiled
client 65740 bytes/SHA 8337949d... with an exact RFC ROM guard; standard/RC2 rebuilds
remain byte-identical per its retained evidence. It deliberately observes TEMT
before EVERY next packet and synchronous output/quit, conservatively forgoing
FIFO-tail overlap; count that cost, do not claim the API requires it. UART's
substantive reply 16-18-23 permits its finite isolated original-ROM functional
campaign within Smith's separate implementation request and existing gates,
retaining startup failure and checking all actually used vectors/receiver binding.
No new runtime result, firmware patch, physical permission or performance claim
is implied here. Firmware artifact/provenance is supplied by Jukebox, not a new
UART-owned build.

Extender EMOS checkout 08301e6d differs from its installed source 5735812e.
Raw syscall25h bypasses ordinary EMOS VDU route selection; first cohort is
Legacy eZ80UART0->mainboard VDP with independent EMOS UART1 keyboard. Preserve
existing extra RX register saves, UART1 parser and VBlank keyboard tick. ExCom,
ExExt and route-aware integration are separate work. Reuse its finite CLI
appliance lifecycle only after actual selected checkout; no bench reservation.

VDPlet reviewed HEAD 10947e04 plus explicit dirty-file hashes. Existing
VDPL-008 client write_buffer/upload/load_module and the 6502 br_exchange donor
use temporary request/sample storage. Adopt a checked 8 KiB ordinary-buffer upload
plus the unchanged numeric module, tagged DONE/call count and byte readback.
Do not create a new renderer/SDK hook. RUN completion does not necessarily
complete queued Canvas work; the correct drawing fence remains separate. This
is a custom-runtime cohort, not a stock-VDP claim.

Rally source checkpoint d4e69d69: road.hpp has a 4096-byte road Stream, but traffic
matrices, GP/HUD/asset helpers and library calls are additional producers.
Do not send the road alone async while those issue ordinary output. Adopt
complete packet controls, 64 Fuji poses/two warmed pages, fixed traffic and motion
work. Whole-frame capacity must be measured; 4096 is road-only. Keep its native
renderer/VDPlet and current TIM-002 timing work as separate cohorts.

MechAgon main e0cdcad5: RAD-02 bytes/plot/gcol/move_tanks use temporary arrays.
Its mode 149 one-tank slice can fit a bounded256-byte persistent packet, with
source-derived 53/65 draw bytes before fence/swap, actual lengths recorded. Keep
networked transport out initially. Preserve per-page XOR history, independent
draw/presentation replies and PRT1 saturation evidence. No-gain is a valid result;
this is not a benchmark of the eventual whole networked game.

## Remaining review boundary

The r02 plan adopts the concrete cohorts above and asks every owner to flag
incorrect source assumptions, missing producer/lifetime constraints, invalid
metrics or unnecessary scope. It does not order their implementation. Jukebox's
explicit implementation exception remains in force independently. Once r02 is
sent to all eight, UART stops for Smith's review; second-round acceptance is
not inferred from delivery. Suite code, deployment, hardware and upstream
publication remain unstarted.

## Second-round disposition and r03

Extender: incorporated public EMOS route admission (not merely fixture-level
Legacy selection) and inactive/write-only-PRT1 restoration limits. VDPlet: kept
bulk readback and numeric result/cumulative count as separate oracles. MechAgon:
kept identical two-fence instrumentation and inline-primitives interpretation.
Nurples: first group must have output-silent behavior or capture its output;
full-frame pipeline is N then N+1, with logical input/pacing alignment; dormant
CALL-patched timer vectors need actual restoration. Fsim: exact-output replay
is separate from legitimate real-time coalescing, and stack reserve includes
foreground plus ISR. Rally: fixed-pose overlap is projection/preparation, not
Motion/Traffic physics; PollFence/steering need separate input/quit observation;
TEMT policy is measured adapter identity. These are narrow source/measurement
corrections, not new firmware features. The r03 task incorporates them and is
returned to all eight for record before stopping for Smith. Remaining bank,
fence, CTS and deployment questions stay open. No runtime gain is claimed.

Jukebox r02 reply (16-25-01) confirms its existing counters do not directly
measure underruns, ISR timestamps, elapsed handoff time or CPU capacity; these
remain future benchmark oracles. Its matched packetized-sync control is not yet
implemented. Four finite functional cells are queued, all unrun at handoff;
this separate task continues without extending UART suite scope.
