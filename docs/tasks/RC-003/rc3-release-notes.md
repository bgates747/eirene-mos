**BREAKING ABI CHANGE FROM RC2: syscall 25h replaces 42h/43h. Existing RC2 clients must migrate or use the startup-fixed RC2.1.**

**THE PINNED RFC STILL HAS THE STARTUP BUG.** Tom Morton's [RFC](https://github.com/AgonPlatform/eirene-mos/pull/2), revision `ffab9c9c84a31535d1ec976b7e6f23b2579ecb80`, initializes the RAM interrupt table before clearing BSS and erases 45 defaults. This fork's RC3 includes the separate [startup correction, PR3](https://github.com/AgonPlatform/eirene-mos/pull/3).

RC3 lets an application calculate while MOS sends its immutable buffer to the VDP using Tom's interrupt-driven 16-byte OTIRX refills. Ordinary RST10/RST18 remain synchronous. This is an experimental fork prerelease while the RFC evolves, not an upstream/stable release or an EMOS installation.

- The first source commit (`b219486`) fixes startup only; this second commit replaces our sender with the pinned RFC implementation.
- One foreground ADL/actualMB0/EI producer, positive full 24-bit source and non-null assembly callback. No queue, BUSY/NULL conveniences or RC2 finish syscall. The raw RFC's A return is IER-derived; do not treat it as an admission status.
- The callback releases source RAM after its final FIFO fill. Physical TEMT and VDP execution are separate. The included C/assembly recipe prearms a flag and drains before ordinary output/exit.
- Tom's CTS wait inside the ISR is retained; it can delay RX, keyboard, VBlank and timers. No bounded-latency or new performance claim is made.

The ZIP contains exact MOS source/binary/map/ELF; matching functional fixture and worked-example sources/binaries; standalone startup checker; pinned target SDK library/headers; build/run/adaptation instructions; raw results, attribution, licenses and SHA256 checksums. Start with root README.md. No modified VDP is required.

Both Flexe engines passed startup, boundary/large-span byte comparisons, 9 callbacks, source reuse, concurrent RX, worked example and CLI return. The two RC3 runs verified 134754 payload bytes; a foreign-ROM refusal control passed. Two clean MOS builds match. These exact RC3 bits have not had a new physical run. Earlier RC1/RC2 CPU/throughput results are not presented as RC3 measurements.

Source/tag: `97311c437093e416342a6c836cf9914f2ced027d` / `3.1.0_uart0_rc_3`. MOS CRC32 `B08C80B8`, 100879 bytes. MOS SHA256 `d7a51147f3381cd68d56f3fbe4605434a897dfae1b049269afeba09ec2b7eb50`.
