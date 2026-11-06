# RC-003 — Startup-fixed RC1/RC2 refreshes and RFC-based RC3

Brandon authorized implementation, qualification and publication on 2026-11-05:
“ok make all that happen. write up the task first. no further approval required
from me.” He additionally directs Jukebox to use our published RC3 as its pinned
MOS when this work is complete. Preserve main and all existing tags/assets.

The result gives existing clients startup-corrected versions of their existing
ABI, and gives RFC users a separate candidate matching Tom Morton's proposed
25h interface. The inherited erased-interrupt-default bug must be corrected in
all three candidates. Existing RC1/RC2 binaries remain historical downloads with
prominent notices pointing to their corrected successors.

REL-001 [x] Freeze exact upstream/RFC/release pins and this plan before source
implementation. Preserve all existing working-tree changes; use isolated source
branches and serial Pi compiler / exclusive Oryx emulator FIFO. Eirene retains
its existing AgonDev toolchain. No physical flashing or bench preemption.

REL-002 [x] From released RC2 commit825eaf77176247f5b5ba2f940ae73fcace34e7e5,
make the first RC3 source-branch commit ONLY the startup-table fix, and push it
before transport changes. This commit also supplies the RC2.1 source tag. Make
an independent startup-only RC1.1 commit from released RC1
47dd56129c0043931bb32f7d329c0392a0b8a809. Do not rebrand or change their sender
ABIs; document unchanged on-screen RC1/RC2 branding and exact corrected ROM IDs.

REL-003 [x] Make the second RC3 source-branch commit replace our 42h/43h sender
with exact RFC leaf/ISR/API implementation pinned to
ffab9c9c84a31535d1ec976b7e6f23b2579ecb80 (PR2, baseeeebe2d). Preserve the
startup correction and ordinary synchronous output. Remove our old transport,
its API declarations/docs/examples, rather than run two engines. Include RC3
branding, accurate caller contract, minimal C/assembly worked example and
matched fixture updates in this second commit. No new guards, queue, cancel,
finish service or CTS policy refinement. Pin RC3 to that second commit after
qualification. Existing historical experiments remain explicitly historical.

REL-004 [x] Build identified source snapshots using the established native Pi
AgonDev under build FIFO; finite serial compilation with logs/pins/maps. Compare
original vs fixed RC1/RC2 sources/objects and startup verifier. Reuse the exact
Console8-qualified corrected RC2 binary if reproduced identically; distinguish
prior physical evidence from new model-only evidence. Provide RC3 ROM/map/source
pins to Jukebox as soon as valid if useful, but final selection follows release.

REL-005 [x] Run a finite matched Flexe functional campaign on Oryx: standalone
IRQ checker on all three images; each ABI's matching functional fixture and
worked example; both engines for RC3 and at least one engine for each refresh.
Reuse existing valid-caller RFC boundary/large-span receiver comparison and
legacy RC1/RC2 regressions. Check exact payload, callback counts, source lifetime,
ordinary output and CLI return, preserved RX and backend/UART errors. Keep a
foreign-ROM refusal control for pinned fixtures. Up to8 cells,300s/cell,
60s no-progress,1800s total, first unexpected failure stop; no soak/performance
expansion or new physical run. Preserve original failure evidence, release Oryx
promptly, immediately steer actual next owner. Source changes after a failed
cell require a fresh finite campaign/reservation rather than silent acceptance.

REL-006 [x] Produce downloadable ZIPs with matching full MOS source, binary,
map, test/recipe source and binaries, brief how-tos, exact source commits and
checksums, retained original copyright/license/credits and scoped evidence.
Verify source reproduces binaries, archive members match manifests and uploaded
assets download byte-exact. Use tags3.1.0_uart0_rc_1.1,
3.1.0_uart0_rc_2.1 and3.1.0_uart0_rc_3. New releases are fork prereleases,
not stable/upstream or automatic EMOS deployments.

REL-007 [x] Publish refreshes and RC3 without moving old tags/assets or main.
Prominently warn RC3 BREAKS RC2 ABI:25h replaces42h/43h; one valid positive
immutable source, non-null assembly callback, actualMB0/ADL/EI, no BUSY/NULL/
finish conveniences, CTS waits inside ISR, callback releases source before
TEMT/receiver completion. Explain old42h/43h clients remain on1.1/2.1. Link RFC
and startup PR3; explicitly state pinned RFC revision still has the startup bug,
which this fork's RC3 fixes. Do not make a moving-head or new performance claim.
Prepend bug/successor notices to old release descriptions, preserving their
original text/assets/tag identities. Record actual repository fork-network
routing, publication receipts and untouched refs.

REL-008 [x] Send Jukebox durable handoff plus immediate steering: select our exact
published RC3 as pinned MOS, with source/ROM/map/archive identities, build/run
contract, startup correction, ABI migration and honest qualification scope.
Brandon authorizes this selection instruction; no new physical flashing or
unrelated app scope is inferred. Notify other existing consumers only with
material artifact/ABI information under standing communication authority.

Task is complete when the three prereleases are verified publicly downloadable
and Jukebox has received its actual RC3 selection instruction. Report physical
qualification limits plainly; do not wait for upstream acceptance or ask for
another release approval.

Completed: [qualification](qualification.md), [publication receipts](publication.json),
[download/package identities](packages.json) and [Jukebox selection delivery](jukebox-handoff.json).
