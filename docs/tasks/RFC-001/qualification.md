# RFC-001 first transfer checks passed

Tom's original proposed sender successfully delivered the tested bytes while
allowing incoming replies and normal return to MOS. Both Flexe engines passed
repeated runs, including transfers larger than 64 KiB. This establishes a useful
functional baseline for application testing. It does not yet answer whether
normal CTS pauses delay audio/input, or how much useful CPU time this version
saves. No hardware firmware was changed.

## What ran

Three finite headless cells on Oryx, actual checkout 314:

| Cell | Invocations | Result | Host duration |
| --- | ---: | --- | ---: |
| Original RFC, JIT |2|PASS|55.01s|
| Original RFC, interpreter |2|PASS|137.90s|
| Foreign published RC2, JIT |1 refused|PASS|7.81s|

Original sender commit ffab9c9c84a31535d1ec976b7e6f23b2579ecb80;
ROM 100824 bytes, CRC32 E07BCF57, SHA256
f2602c0319ff2b1a47942dabcf6c66c696a9de4ce0702e4bda8b9e677f4dc7ac.
Fixture 22445 bytes, SHA256
6d487f59cbb727e5bb6a38059cc4d73be4d3ec408296466dfe803454e7c393ae.
Full build, runtime/receiver and private canonical verifier pins are retained
in fixture-build.json, stopped-profiles.json and the archive.

Every normal invocation tested raw borrowed lengths 1/15/16/17/255/256/257/1024,
then a 67588-byte framed source carrying 65536 payload bytes. This exercises a
24-bit length above 65535 and a source crossing a 64 KiB address boundary in ADL.
Each case produced exactly one callback. Total: 36 accepted transfers/callbacks,
269508 payload bytes checked independently against the emitted wire and through
existing receiver conditional comparisons. Wrong-byte and right-byte receiver
controls passed before the normal cases. Source overwrite after callback and
before the explicit TEMT wait preserved receiver contents. This ordering does
not claim that the first overwrite necessarily preceded physical drain.

Each large case observed the GP reply before source release. After the last
transfer, ordinary MOS output/query and all three required active IRQ vectors
passed. Both engines created R0001/R0002 with next.txt=3, proving normal repeat
invocation and report numbering. Four retained reports are in model-reports/.
Both whole runs reached the real CLI-return marker; no synthetic target output
was used as evidence. All backend failure/unhandled/unregistered/unmapped and
UART drop/overrun counters were zero.

The foreign-ROM case refused before report creation or async case entry and
returned an error through MOS's normal autoexec abort at line 2. That expected
abort is the negative-control outcome, not a test failure.

## Scope and limitations

- Original firmware is unmodified. Its inherited default-vector initialization
  defect remains; this fixture reads the three actually used vectors and never
  dispatches the erased defaults. No general startup qualification is claimed.
- Initial caller is ADL/MBASE0, interrupts enabled, one producer, persistent
  source and small AF-only assembly callback. No C callback, null callback,
  zero/overlap, banked Z80 or cancellation contract was qualified.
- Completion flags were armed before submission. All reported early-callback
  observations were 0; no forced callback-before-wrapper-return race is claimed.
- No keyboard events, audio playback, rendering load or finite CTS pause was
  deliberately injected. RX-during-TX is a GP reply, not an input-latency test.
- Model host durations are useful scheduling estimates only. They are not eZ80
  throughput, retained CPU capacity, physical timing or optical presentation.
- Retained actual-firmware receiver uses stock buffered commands, but its
  identified diagnostic binary is not represented as stock VDP firmware.

## Evidence and handoff

Pi and Oryx hold the checksum-verified complete archive:
`build/rfc001/first001-evidence-complete.tar.gz`, 12547272 bytes, SHA256
`ce60daa6107e54af80fb8086bc385db0c11477e4fc2a3595e7fe8c23cdbbf7dc`.
It includes stopped profiles/runtime, private FAT images, raw wire/stats,
reports, frozen app sources/Makefile/identity, ROM/map, compile/disassembly
logs and the actual runner/verifier. The initial archive remains preserved.
The source files listed in the build manifest were reverified after retrieval;
the local independent oracle rechecked all four actual wire streams and reports.

The private frozen canonical Pi verifier passed; no shared Oryx tool was patched
or check bypassed. All owned processes stopped, fresh whole-host inspection was
empty, checkout 314 released and the actual next Jukebox E02 owner immediately
notified. Full receipts are oryx-checkout.json and oryx-release.json.

First transfer-validation tranche is complete. Next planned tranche is realistic
finite CTS/RX/input/timer latency qualification, followed by matched throughput
and foreground-work measurements. The new emulator-related changes remain
uncommitted pending the standing human-validation gate. No new sender variant,
card deployment, physical flashing or upstream publication occurred here.
