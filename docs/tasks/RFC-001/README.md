# RFC-001: qualify Tom Morton's proposed background UART sender

We want to find out whether Tom's proposed MOS service lets real games and
players spend less CPU time sending data, without losing bytes, responsiveness
or sound. Compare identical workloads with ordinary output and background
sending, then use application measurements to show where the saved time helps.
This is a review plan, not a claim that the new proposal is already qualified.

Revision r04, 2026-11-05. Owner feedback and dispositions are in
[feedback.md](feedback.md); immutable replies are retained in owner-replies/. Smith authorized the first transfer-validation implementation tranche on
2026-11-05; see [first-tranche.md](first-tranche.md). Later performance/app and
hardware deployment gates remain separate. Smith separately instructed Jukebox to write and execute its
migration task immediately. All other recipients may inspect their own code and
advise on integration and benchmarks; this request does not start their builds,
bench runs, firmware changes or publication.

## Pinned proposal and limits

[RFC PR #2](https://github.com/AgonPlatform/eirene-mos/pull/2), Tom Morton,
head `ffab9c9c84a31535d1ec976b7e6f23b2579ecb80`, base
`eeebe2d34cf2941b0686d923d762378a7811b021`. Body, comments and reviews were empty
at inspection. [The proposed diff](reference/proposed.diff) is retained locally.
Recheck the head before implementation; record changed contracts and affected
reviews rather than quietly testing a newer revision under this pin.

The proposal already uses OTIRX, with 16-byte refills in MOS's UART interrupt
handler. Syscall **25h** takes HL=source, BC=length, DE=callback. Ordinary RST18
remains synchronous. This is not our published RC2 submit 42h/finish 43h API:
there is no finish service, queue, BUSY guard or documented cancellation.
A callback releases the borrowed source after its final FIFO write; it does
not certify the UART is empty or the VDP has executed the command. Keep a
single producer and immutable outstanding packet in application adapters.

The callback runs inside the ISR. Begin with flag-only assembly callbacks;
qualify any C bridge and alternate-register, IX/IY, stack, MBASE and return-mode
requirements against actual code. Do not let an application's pacing ISR become
a competing UART owner. Application teardown and normal VDU output need an
explicit, reviewed serialization/drain recipe appropriate to this API.

Source-review questions to reproduce or resolve, not yet measured RFC defects:

- The return comment promises A=0, but submission leaves the IER value in A.
- Zero length, a null callback and overlapping submissions have no guards;
  keep them out of normal app tests until contract and isolated probes settle.
- WAIT_CTS spins with interrupts disabled during refill: qualify finite pause
  recovery, RX coexistence and latency before considering a sustained stall.
- ADL/Z80 callback selection uses MBASE; check bank lifetime, upper count bits,
  mixed-mode return and callback clobbers instead of copying RC2 assumptions.
- The pinned base still initializes RAM interrupt vectors before clearing BSS.
  IRQ-001 already demonstrated this ordering defect in our earlier base. Check
  section placement and startup on the actual RFC build before any card staging;
  keep exact-proposal evidence and any narrowly corrected variant distinct.

## Selected Nurples baseline — RC3, 2026-11-05

Brandon selected our tagged RC3 for Nurples APP-001. Use this image for BOTH
packetized synchronous and async controls; the original uncorrected RFC ROM
remains historical reference evidence, not the selected deployment baseline.

- Release: [3.1.0_uart0_rc_3](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3).
- Source commit: `97311c437093e416342a6c836cf9914f2ced027d`.
- MOS: 100879 bytes; CRC32 `B08C80B8`.
- SHA256: `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
- Startup fix followed by the exact pinned RFC25 sender; RC2 services 42h/43h
  are absent. [RC-003](../RC-003/README.md) records builds, maps and qualification.

Nurples' canonical application checkout is now
`/home/smith/Agon/mystuff/nurples-repair`, branch `dev`; the old checkout is
retired. Selection and checkout provenance are in durable mail
`2026-11-05_22-34-38_nurples_rfc001-rc3-baseline-human-selection`.

This is private experimental use pending the RFC's merge, not approval for
broader adoption. A public prerelease download does not change that limit.
Existing original-RFC model/app results retain their original firmware identity;
none becomes an RC3 result through this selection. CTS/DI latency, MBASE and
callback constraints, distinct source/TEMT/receiver completion, matched workload
accounting and further performance/hardware gates remain in effect. This plan
update does not authorize new hardware or emulator execution.

## Review distribution

| Project | Scope of requested input | Existing chat |
| --- | --- | --- |
| Nurples | First game integration, draw/output seam, assembly callback recipe | Locate Purple Nurples project |
| Fsim | Render packets, computation overlap, frame-time and input latency | fsim 2026-10-08 6.1 Sol |
| Wolf | Renderer packets, memory/banks, frame-time and input latency | Wolf3dOrig |
| Jukebox | Execute authorized RFC migration; compare its existing RC2 player | Jukebox 2026-09-07 |
| Extender | EMOS/legacy integration, size constraints and test-appliance fit | Extender 2026-10-13 Sol |
| VDPlet | Packet ownership, receiver execution/ack boundaries and SDK fit | VDPlet 2026-11-04 |
| Rally | Render/output boundary, compute overlap and race responsiveness | AgonArcade 2026-10-14 |
| MechAgon | Early-stage feasible consumer and minimal useful benchmark | MechAgon |

Each owner should cite actual files/functions and source revision; identify
buffer ownership, direct-output conflicts, timers/DI/MBASE, callback and quit
handling; propose the smallest useful workload, baseline, metrics and pass/fail
conditions. State blockers and unavailable features honestly. MechAgon's
immaturity calls for a small feasible slice, not a prerequisite feature project.
Return substantive durable mail on thread `uart-rfc001-suite` to `agon-mos`.
No recipient is asked to redesign firmware or expand its existing scope.

## Refined test order and shared decisions

First qualify a small valid ADL/MBASE0 single-producer caller, then run controlled
CPU/throughput measurements, then the minimal game/SDK cohorts below. Broader
classic/Z80 support and invalid inputs remain separate ABI questions. Do not
require extra firmware features, cancel services or a resident test framework.

Use three application controls where packetization changes existing code:
legacy fragmented synchronous output (diagnostic reference), packetized
synchronous output, and the identical packetized async output. The decisive
pair runs on the SAME RFC MOS/receiver with identical bytes, useful work and
quality. Also retain pinned base synchronous results to detect base/build
changes. Packet-construction/copy costs and TEMT barriers stay inside measured
whole-frame totals. Our RC2 remains a distinctly pinned comparator.

One app owns all output, including HUD/debug/query/swap/quit. Stack-local or
self-modifying command helpers must be copied to persistent packet storage;
replacing a global send function is unsafe. Two app buffers may allow preparing
the next packet while one is in flight; this adds no MOS queue or second
outstanding submission. Preparing next-frame state must not overwrite the
current frame's still-needed scene data.

Arm pending receiver tokens as well as TX completion before sending requests.
A receiver reply and TX callback can be observed in either order: retain both
independently. Define a selected receiver's ordered fence explicitly; TEMT is
only the local wire-empty observation. For stock drawing, review existing CA
flush followed by a fresh matching query reply; for VDPlet use its operation's
tagged reply and a drawing fence where needed. Neither is optical scanout.
No blind query with stale flags or competing outstanding tokens is acceptable.
At quit stop production, reconcile source release, required drain/receiver work,
then restore callbacks/timer/display and return. A failed wait does not cancel
the sender or permit freeing its live code/data.

Use an unowned timer appropriate to each app, record its width/prescaler/wrap or
saturation and restore it. Do not appropriate Jukebox's pacing timer. Serviced
VBlank/PRT IRQ ticks can be lost during DI; use independent observer elapsed
bounds for finite CTS tests. A foreground-observed callback flag supplies an
upper bound on callback time, not its exact ISR timestamp. Overlapping elapsed
phases cannot be summed as disjoint CPU-time buckets.

Measure linked text/ROM end, BSS and app packet RAM separately using the same
compiler/configuration; declared RFC BSS is 11 bytes before link padding. Keep
EMOS RX/UART1/keyboard behavior intact. EMOS's first cohort is Legacy physical
UART0 to mainboard VDP; ExCom/ExExt route-aware integration is separate work.

Jukebox has now built the exact original RFC (no firmware patch): 100824 bytes,
CRC32 `E07BCF57`, SHA256
`f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac`.
Source/map/toolchain proof and ROM are in
`/Agon/mystuff/AgonJukebox/docs/tasks/UART-004/original-rfc-build-artifacts.tar.gz`.
Its linked startup verifier reproduces the inherited vector/BSS failure.
That known expected failure must remain visible in any isolated original-ROM
functional campaign; it is not a startup-qualified/hardware-ready image. For
Nurples' selected deployment cohort, RC3 supplies the startup correction to both
matched controls, as pinned above. This supersedes the earlier unresolved
startup decision for APP-001; the original-ROM evidence remains unchanged. No
physical test is started by this plan update. Jukebox's own implementation/qualification remains separately
authorized; it conservatively waits for TEMT before every next packet and will
report that prototype overhead rather than call it an API requirement.

## Planning and review gate

PLAN-001 [x] Read and pin the RFC implementation and examples; distinguish it
from the older attachment and our released RC2.

PLAN-002 [x] Obtain eight owners' source-grounded integration/benchmark feedback.

PLAN-003 [x] Collate common requirements, app-specific exceptions and unresolved
questions in feedback.md; revise this plan with explicit dispositions.

PLAN-004 [x] Send the refined plan to all eight owners for review, then stop for
Smith's review. Record actual delivery and reply state, not acceptance by inference.

## Implementation tranches

ABI-001 [x] Make a minimal command-line appliance and worked ADL callback example;
prove source order, exactly one completion, immediate-completion flag arming,
normal output after drain and repeat invocation. Include lengths 1/15/16/17,
255/256/257, 1024 and valid large spans. Preserve expected/actual byte checks,
not just sender callback counts. Reuse existing fixtures rather than building
another framework. A classic/Z80 case follows only after the bank contract is clear.

The RC3 responsiveness/performance continuation is now authorized; its finite
implementation and execution gates are in [second-tranche.md](second-tranche.md).
This does not grant physical deployment or another release.

ABI-002 [ ] Qualify registers/stack, RX/keyboard coexistence and finite CTS pauses
under realistic graphics/audio traffic. Distinguish source release, TEMT and
receiver acknowledgement. Isolate any deliberately invalid-contract probes with
an external bound/recovery path; do not make hobby-computer crash-proofing a
release prerequisite or add defensive MOS code merely to satisfy invented tests.

PERF-001 [ ] Compare ordinary synchronous output and async output on the same
RFC build using identical payloads and receiver commands; retain pinned base
ordinary output as an additional baseline.
Keep our released RC2 as a separately pinned historical/migration comparator.
If the base needs a startup correction, run matched controls with that same
correction and label them; do not attribute base/toolchain changes to async.

PERF-002 [ ] Measure three independent questions: flat-out payload/wire throughput;
foreground work left during flat-out sending; foreground work at average 44,100
payload bytes/s with the same 256-byte chunks. Also reproduce Tom's idle-versus-
sending tight assembly counter over a fixed number of VSyncs. Use proposed ten-second windows with three repeats per controlled cell,
subject to actual counter/wrap/buffer limits and observed run durations; retain
first unexpected failure and stop that cohort. This replaces reliance on the
earlier ~77ms bulk sample. Record
actual elapsed time, missed pacing deadlines, pauses and completion/drain time.

PERF-003 [ ] Calibrate the identical foreground work loop without sending, then
report retained capacity R=(work/elapsed)/(idle_work/idle_elapsed), foregone
capacity 1-R, percentage-point and relative changes with their denominators.
A blocking caller doing zero foreground work is not proof the CPU executes UART
code 100% of the time. Count callback and adapter overhead consistently. Report
payload versus wire bytes separately (1,152,000 baud, 8N1 gives 115,200 wire bytes/s).
PRT and VSync checks help validate accounting; emulator timing is not hardware
performance, and shared clock sources are not independent clock calibration.

APP-001 [ ] Use Brandon's selected tagged RC3 baseline above for Nurples, with
both matched controls on that same MOS. Use a repeatable scene,
seed/input trace and fixed quality. Start with move_sprite_group sprite packets
as an integration proof, then a larger full-frame/earlier packet overlapping actor
updates as the performance case: the late sprite-only seam may only overlap
VBlank waiting. Use two dedicated static buffers rather than mutable @cmd
helpers. Proposed finite scene: 1200 frames/120 warmup, fixed seed 0x50. The first selected group must
be output-silent throughout its behavior (or capture behavior-side output too);
no spawn/death alone does not suppress laser/fireball animation or seeker
commands. Include those actors/player/tile/HUD producers in the full-frame case.
Compute/build N, submit N, then overlap only independent N+1 update/build work;
match logical frame/input/pacing schedules across both controls. Compare synchronous and async
versions with identical graphics, collision/update work and output; stock VDP,
no affine-sprite experimental dependency. Measure actual FPS/frame
latency plus CPU render/update/submit/wait slices and bytes/frame.

APP-002 [ ] Apply the same principles to Fsim, Wolf and Rally, using their owners'
proposed packet seams and workloads. Avoid changing render quality or moving
work onto the VDP in only one comparator. Record input/quit responsiveness and
receiver correctness alongside median/tail frame times.

APP-003 [ ] Incorporate Jukebox's separately authorized RFC variant. Test fixed
tracks/rates, fractional EOF, skin/analyzer changes, pause/stop/quit and source
packet lifetime. Record underruns, callback counts, audio integrity, foreground
headroom and timer restoration; throughput alone is not successful playback.
Retain its old RC2 results without relabelling them as RFC25 results.

APP-004 [ ] Extender: qualify Legacy UART0 only and preserve the existing RX,
UART1 keyboard/parser and VBlank tick paths. Reuse its finite CLI appliance and
restoration protocol after a separately selected physical checkout; no current
bench lease is requested. Record actual merged ROM/RAM cost.

APP-005 [ ] VDPlet: deterministic ordinary-buffer upload with 256-byte chunks,
finite 8 KiB, existing numeric module preloaded outside timing, checked tagged
RUN result/call count and existing byte readback. Keep RPC latency distinct from
TX throughput. This cohort needs a named custom VDP runtime, not stock firmware;
no new native module/runtime hook is required.

APP-006 [ ] MechAgon: reuse RAD-02's mode 149 grid and one hardware tank with
fixed R120/45-degree filled sweep or line boundaries, per-page XOR history and
a persistent bounded 256-byte packet. Setup/logging/teardown stay outside timed
intervals equally. Measure actual encoded bytes, draw reply and presentation
reply separately. Exclude network transport/VDPlet migration and any claim about
the unfinished game's eventual whole-system workload.

APP-007 [ ] Rally: existing STANDARD direct-eZ80 renderer and stock VDP, 64 fixed
Fuji poses plus two warmed pages, traffic/player/HUD and complete frame bytes.
Build identical whole-frame packet controls; road-only 4096-byte Stream is not a
proven whole-frame capacity. Repeat fixed pose cycles for a useful finite window;
the fixed-pose donor's overlapped work is next-pose projection/packet
preparation, not its bypassed live Motion/Traffic physics. Observe interactive
input/quit separately; fixed poses ignore steering and PollFence waits do not
service foreground ESC. Record every TEMT-barrier policy as adapter identity. Native/VDPlet
renderers remain separate cohorts.

APP-009 [ ] Wolf: prove the r07 bespoke 24-byte pose+render packet first, then
its separate VDPlet 65-wire-byte transaction (not merely 28-byte payload). Use
canonical enemy-free E1L1 tile 34,36 and fixed HUD/assets; 600 pose capacity and
paced coalescing are distinct tests. Match native DONE and presentation tokens,
retaining receiver generation state after TX release. Exclude older A timing
results missing INIT_LEVEL/map binding; corrected r07 is the workload donor.
No inference from VDP draw cycles or outstanding emulator clock disagreement.

APP-008 [ ] Fsim: fixed airborne Corsair pose/background/input trace, same render
module/quality and physics work. Persistent packet copies replace stack 37-byte
requests and pose headers; scene/frame storage additionally remains owned until
matched receiver completion. Keep PREPARE/RENDER/presentation phases intact.
For exact-output checks replay identical captured pose packets/work; for the
separate real-time observation preserve original 30 Hz/coalescing and compare
state at matched simulation ticks, reporting scheduled/serviced/dropped steps
and input gaps. A different legitimately coalesced presentation subset is not
by itself byte corruption. Check actual foreground-plus-ISR stack reserve using
the owner's existing guard, not just ROM/BSS totals; do not claim that
transport restores asynchronous receiver rendering. Avoid paused rolling/contact
work and any disguised controller-API migration.

PKG-001 [ ] Package pinned MOS/app sources, binaries, hashes, worked recipes and
finite expected-duration instructions together. Keep full history in project
space, short current readme.txt on the card, sequential collision-free reports
and one known active test path. Provide direct no-switch application invocation
and run-all where suitable. No SD write or firmware flash is authorized now.

HW-001 [ ] After source/fixture review, prepare the minimum meaningful Console8
manual qualification with stock VDP wherever possible. Explicitly identify any
app requiring matched custom firmware. Extender alone coordinates live Olimex
checkout. Pi compiler FIFO and Oryx emulator lease rules remain; this plan does
not reserve machines, interrupt another owner or waive human approval gates.

## Second-round review clarifications incorporated

These narrow changes incorporate actual r02 replies, not new sender features.
The reviewed r02 documents/hashes remain in reviewed-r02/; verbatim second-round
mail remains in owner-replies/. This r03 is returned to the same distribution
for record, then UART stops; no further review loop or execution is started.

- EMOS's public merged entry must preserve committed routing: its owner must
  define Legacy-only admission/refusal or an already route-aware integration,
  serializing mode transitions against outstanding sends. A fixture promise
  alone cannot make an unrestricted UART0 syscall safe in general EMOS.
- The optional polling PRT1 donor accepts only inactive system-clock PRT1 with
  proven ownership/source, leaves it disabled, and cannot promise restoration
  of an unknown write-only reload. Use an existing other clock if it is owned.
  Do not activate Nurples's dormant CALL-patched PRT vector without restoring
  its exact prior vector bytes and source state under a documented timer contract.
- Keep VDPlet upload byte readback distinct from its unrelated numeric oracle;
  freeze variant 1/input 2.0 -> 3.25 (`0x40500000`) and cumulative call-count baseline,
  including warmups. Readback is outside TX timing and inside total run duration.
- Keep MechAgon's two draw/presentation fences identical across arms. Its chosen
  mode 149 ordinary primitives execute inline before ordered C3; faster producer
  return need not shorten frame cadence or imply a queued raster backlog.
- Explicitly preserve Nurples N-to-N+1 pipeline scheduling, Rally's projection
  rather than physics overlap, and Fsim's deterministic-versus-coalesced-real-time
  distinction as specified above. None justifies adding runtime hooks.

## Existing evidence to reuse

- [TM-001 performance comparison](../TM-001/hardware-perf2-r01.md),
  [TR-001 lean hardware results](../TR-001/hardware-results.md),
  [IRQ-001 startup regression](../IRQ-001/hardware-results.md).
- `experiments/uart0-performance2/src/{main.c,platform.c,api.src}` and its metrics
  scripts: reuse the useful-work denominator and receiver checks.
- RC2 reference tag `3.1.0_uart0_rc_2`, commit
  `825eaf77176247f5b5ba2f940ae73fcace34e7e5`, ROM CRC32 `9E08D539`.
  Its hardware result (~86% retained foreground capacity during its bulk+work
  workload) neither qualifies this RFC nor guarantees a matching application gain.

Review handoff: r02 and final r03 delivered to all eight existing chats; actual
receipts are in refined-plan-deliveries.json. UART stopped for Smith review.
Delivery does not imply implementation approval or complete second-round replies.

Execution update: first transfer fixture compiled and host checks passed;
original-RFC target runs are queued. See first-tranche.md and fixture-build.json.
This supersedes the earlier planning stop for that tranche only.

First-tranche completion: original-RFC functional checks pass in both Flexe
engines plus wrong-ROM refusal. See [qualification.md](qualification.md).
Finite CTS/input-latency, performance and application cohorts remain next work.
