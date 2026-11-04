# IRQ-001 Console8 deployment — 2026-11-04

The Author authorized SD deployment. The matched before/after appliance is at
`/test/mos-uart0` on the Console8 card mounted on Oryx at
`/run/media/smith/AGONC8`, label AGONC8, vfat UUID8658-1C23. The existing folder
was archived and each tar member checked before replacement. The returned
archive and manifest were copied to Pi and verified there as well as on Oryx.

Archive: `build/tm001/irq001-deploy001/returned.tar.gz`, SHA256
`17bc957e5941d683b5f97d607db2de0db27083dacd6bf7eacd0a12b14382beb4`.
It preserves all old firmware/apps, R0054–R0059, counter60 and the complete prior
running log. On-card history is reduced to a short deployment journal; the
full history stays in project archives. No previous results were new/unreviewed.

The new card files exactly match the qualified package, except the intentionally
updated deployment guide/checksum manifest and new counter/deployment records.
Before starts at60; after starts at62. With one completed pair per image and the
prescribed test/test/example/perf sequence, expected reports are before I0060/61,
after I0062/63 and after R0064/65/66. Counters are independent per case directory;
retries increment them and never replace an existing report. The standalone
example writes no report. Full file hashes are in [deployment.json](deployment.json).

Both MOS binaries are100950 bytes. Before CRC9E08D539; fixed CRCDBE3E21E.
Their banners remain identical; the fixture verifies the actual installed ROM.
The stock Bistromathics2.16.0 VDP and official stock MOS restoration binaries are
included. Use the installed normal flash MOSlet with its normal checks. Read
[the exact on-card guide](deployed-readme.txt) for the manual boot/reset sequence.

Only the UART appliance folder was replaced. Root MOS, autoexec, boot script
presence/content and installed flash MOSlet are unchanged. Files were synced and
read back. The card remains mounted; no remount, ejection, firmware flashing or
physical test was performed. Model qualification remains recorded in
[qualification.md](qualification.md); this deployment does not imply a hardware
pass. No upstream communication, tag/asset replacement or main merge occurred.
