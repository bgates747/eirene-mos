# RC3 single-buffer C recipe

Requires startup-fixed RC3 installed; this is syscall25h, not RC2's42h/43h.
Run `example` with no switches. Expect RC3 EXAMPLE PASS and immediate return.
The source, callback and flag remain resident through source release and TEMT.
A callback before submit returns is valid; the flag is armed first. A work count
of zero is also valid for this short message. No performance claim is made.

The assembly bridge loads HL/BC/DE and calls25h. Its primary-register-only
callback stores a flag and returns; the C foreground does useful work until
that flag, then polls TEMT before ordinary output/exit. See docs/uart0-async.md
for single-producer/actualMB0/EI and independent receiver completion obligations.

Build with `make AGONDEV_TOOLCHAIN=/absolute/path/to/agondev`. No generated
headers or ROM allowlist are required; installing the documented matching MOS
is a deployment prerequisite. Do not use this example against RC1/RC2.
