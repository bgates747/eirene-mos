# RC3 valid-caller regression fixture

This preserves the original RFC fixture's byte oracle:1/15/16/17/255/256/257/1024
byte sources plus67588 bytes framing65536 payload bytes, one completion per
source, immediate source reuse after callback, concurrent RX and ordinary output
when drained. It measures correctness, not speed. Do not test invalid/null/zero
or overlapping sources against the raw RFC.

The release package contains a generated identity.h and packets.h matching its
MOS/map, source and binary. Run `test` in its writable directory; it clears the
screen, prints progress and writes sequential Rnnnn.log reports. Allow about
two minutes; a stall is failure. A foreign ROM is refused before syscall25h.
Build with the existing AgonDev Makefile. Source-generation/build provenance and
exact pins are supplied in the release package. No custom VDP is required.
