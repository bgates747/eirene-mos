# RC-003 complete — startup-fixed refreshes and RFC25 RC3

Applications retain their existing RC1/RC2 contracts with RC1.1/RC2.1; RC3
adopts Tom Morton's proposed25h sender with the startup correction. All three
are published fork prereleases. Original tags/assets and main are unchanged.

Source order is exactly the Author's requested sequence. RC3 starts at released
RC2 825eaf7, first commit b219486 moves only the initialization call and was
pushed before transport work. Second commit97311c4 replaces the old engine with
exact ffab9c9 serial/ISR/API source, RC3 branding and matching examples/docs.
Tag3.1.0_uart0_rc_3 pins that second commit. RC2.1 pins b219486. RC1.1 independently
pins d268d0b, a startup-only change from released47dd561.

Original RC1/RC2 rebuild byte-exact with the original target libagon.a04e34018
and the established native compiler. The current installed SDK library5de78783
would add unrelated15 image bytes and3 BSS bytes; that first attempt is retained
under build/rc003/native, with its later fixture-generator map-label failure.
Only the unreleased second source commit was amended to use exported RFC map
symbols. Final frozen builds are build/rc003/native-r02. In each refresh, only
src/init.asm and init.o change versus its matching original; sender and size
are unchanged. RC2.1 is byte-identical to the earlier Console8-qualified corrected
image. RC3's two clean builds match. No official ZDS II MOS was migrated or built.

Five actual Oryx cells passed: RC1.1/JIT, RC2.1/JIT, RC3/JIT, RC3/interpreter,
and RC3's foreign-ROM refusal control. Every positive cell ran the standalone
startup checker, matching UART functional app and worked example, then returned
to CLI. Legacy candidates each verified8192 payload bytes; RC3 each verified
67377 across9 valid sources/callbacks, including67588 source bytes with65536
payload bytes, concurrent RX and immediate source reuse at observed release.
Total receiver-verified payload151138. Independent byte oracle matched both RC3
wire streams; backend errors and UART drops/overruns were zero. Wrong-ROM control
refused before reports or submission. No new performance or physical run is claimed.

Raw reports, wire streams and stats: build/rc003/evidence/. Exact source/image/
map/toolchain/SDK hashes: build-info.json. The frozen SDK dependency is bundled
with notices for reproducibility; no unverified SDK version is asserted. A probe
of official v0.22 found a different target-library hash, so it was not used.

All three release ZIPs and checksum assets were downloaded and byte-compared.
Their tags resolve to the expected source commits. Old release descriptions
received successor/bug notices; original asset IDs/digests and tag/main refs
match the captured originals. publication.json retains actual receipts.

Jukebox was instructed to select published RC3 through durable mail and an
immediate native chat delivery. Exact source, ROM/map/ZIP hashes, actual table
baseBC386 (not current-SDK BC389), ABI/drain and qualification limits were given.
Receipt: jukebox-handoff.json. Its existing original-RFC app results remain
separately identified; selecting RC3 does not relabel old results.

Pi compiler187 and Oryx319 are released, with actual successors notified
immediately where present. No Console8 card, physical firmware, EMOS owner tree
or other project's source was changed.
