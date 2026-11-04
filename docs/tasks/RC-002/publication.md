# RC2 published — 2026-11-04

[Eirene MOS 3.1.0 UART0 RC2](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_2)
is published as a prerelease, not stable/latest. The trimmed implementation
preserves measured performance with fewer MOS instruction bytes. RC1 remains
the verified, more guarded alternative; its tag, assets and evidence are intact.
Main remains upstream. RC2 tag/source is825eaf77176247f5b5ba2f940ae73fcace34e7e5.

[Download the ZIP](https://github.com/bgates747/eirene-mos/releases/download/3.1.0_uart0_rc_2/3.1.0_uart0_rc_2.zip)
(1531674bytes). It contains the complete frozen MOS, regression fixture, C example
and stock/RC1/RC2 benchmark sources and binaries, plus licenses, raw hardware
results, build identities and checksums. The root [README](package-README.md)
explains installation/building, how to adapt the example into an application,
fixed-target C callback gates, caller obligations and metric interpretation.

MOS CRC329E08D539;100950bytes, SHA256
a47130d78b70fa1e0e54aa61e4340831036d766a0c59e2738935bd9d04b94a3a.
ZIP SHA25648d2fefa319f174ab4368287e40743c7610a3aeac61c0e32653fa26858166cd4.
Both uploaded asset digests match local files; the uploaded ZIP was downloaded
and byte-compared before publication. Archive integrity and every manifest
entry were verified. Full source/build/package/receipts are mirrored at
build/tm001/rc2-001 on Pi and Oryx. The executed build script is retained here
for provenance; use the package README's portable Makefile recipes to rebuild.

Two clean RC2 builds match. The only MOS source change from hardware-tested
TRIM Trial1 is version.h; only main.o differs. Sender and every other checked
MOS object match the hardware-qualified implementation. All new benchmarks
share the qualified compiled C measurement/timer core, and stock/RC1 benchmark
binaries remain byte-identical. The fixed C gate object matches the qualified
29-byte gate. Generated app labels/CRC guards target the new RC2 image.
No exact branded-image physical or emulator rerun is claimed. That distinction
is explicit in both release notes and ZIP README; prior hardware evidence is
preserved without changing its identities. No card deployment/physical flash
was done for this publication step.

The syscall numbers remain42h/43h, but RC2 no longer validates broad context or
foreign UART ownership. Foreground ADL1/MBASE0/EI, normal UART setup and sole
ownership are caller preconditions. Extra callback index/alternate-bank saves
move into the supplied app gate. RC1 applications must review those differences.
[Release notes](release-notes.md); [full publication receipt](publication.json).
