# Standalone attachment validation

The new single-file assembly checker is 734 bytes; the exact same binary
reproduced 45 erased defaults on original RC2 and reported PASS on the one-call
startup correction. Both actual Flexe/JIT cold-boot cells passed in about 7.3s
and 7.2s. The expected original exit 1 stopped autoexec at its second line; the
fixed exit 0 continued through the explicit return marker. Backend failure/
unhandled/unregistered/unmapped and UART drop/overrun counters are zero.

New minimal binary SHA256:
58aabd76daa9b3f434e4b33de67e4693a440e318d0ad0174edba7bbbec437323.
Source/binary/MOS/runtime/toolchain/ZIP hashes and member verification are in
attachment-manifest.json; raw evidence is retained at
build/irq001-standalone/evidence/ in this project. Build/runner scripts remain
there; none are required to compile or run the attached standalone assembly.

The original/corrected MOS pair is the previously Console8-qualified RC2 pair,
CRC32 9E08D539/DBE3E21E; this new binary has not itself been run on hardware.
The historical detailed fixture's physical proof remains hardware-results.md.
Runtime used the pinned actual-ESP32 VDP diagnostic backend, not a stock-VDP
fingerprint or new throughput measurement. The checker only uses ordinary text
output; its run protocol needs no custom VDP. Pi build 179 and Oryx 316 released;
actual next owners were notified immediately with steering.

The patch applies cleanly to retained upstream Eirene eeebe2d34cf2941b0686d923d762378a7811b021.
No upstream report, PR, asset upload or release publication has occurred.
