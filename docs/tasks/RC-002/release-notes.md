RC2 lets an aware application calculate while MOS sends its buffer to the VDP using UART interrupts and up to 16-byte OTIRX refills. Normal startup and synchronous RST18 behavior remain unchanged.

This is the smaller successor to RC1: **286 sender instruction bytes versus 476**, with performance preserved in the matched Console8 comparison. The tested implementation retained about **86% of its no-traffic calculation rate during flat-out sending**, and completed **64.6% more paced foreground work than official stock MOS**. Bulk throughput was essentially unchanged; three short repeats do not establish a sustained speedup.

**RC1 remains the verified, more guarded alternative. Its tag, binaries and evidence are unchanged.** RC2 trusts foreground ADL1/MBASE0/EI and exclusive normal UART ownership instead of checking them. Extra IX/IY/alternate-register callback protection moves to a 29-byte application gate supplied with the C example. Applications using RC1 must review this changed contract.

The downloadable ZIP contains complete frozen MOS source/binary/map; matching regression and C-example sources/binaries; stock/RC1/RC2 benchmark sources/binaries; installation, build and adaptation how-tos; raw results; licenses and checksums. Start with its root **README.md**. No VDP modification is required.

Two clean RC2 builds match. Relative to the hardware-tested trimmed implementation, only `version.h` and the banner-emitting `main.o` changed; the sender and all other checked MOS objects are identical. The exact new RC2 branding has not had another physical run. Stock VDP identity and visual/example checks are operator evidence as documented in the bundle.

Source/tag: `825eaf77176247f5b5ba2f940ae73fcace34e7e5`. MOS CRC32: `9E08D539`.

A prerelease in bgates747's fork, based on Tom Morton's Eirene 3.1.0_beta_1 and supplied sender; not an upstream or stable MOS release. Main remains unchanged.
