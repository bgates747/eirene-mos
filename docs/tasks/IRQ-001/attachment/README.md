# Eirene interrupt-default startup check

Prepared by Codex on behalf of Brandon. MIT license; see LICENSE.txt.
The vector layout comes from MOS/Eirene by Dean Belfield, Tom Morton and
contributors.

Copy `irqcheck.bin` to an SD-card directory. Immediately after booting Eirene,
change to that directory and type:

```text
irqcheck
```

Before the patch, expect:

```text
IRQ BUG REPRODUCED: 45 default entries erased; 3 active entries valid.
```

Apply `fix.diff`, rebuild MOS using its normal build, reboot, and run the
**same binary**. Expect:

```text
IRQ PASS: 45 default entries valid; 3 active entries valid.
```

It returns immediately. No arguments, custom VDP or companion files are needed.
Exit status is 0 for PASS, 1 for the reproduced bug, and 2 for unexpected or
unsupported contents. A command script may stop at the expected nonzero result.

This read-only checker neither executes nor changes interrupt entries, resets,
flashes, nor writes files. Run before installing custom interrupt/RST hooks.
It discovers the table through Eirene's ROM vectors and checks defaults against
the fresh-boot RST20 handler. This is a table check, not peripheral IRQ stress.
Mainstream ZDS II MOS has a different layout and does not have this defect.

## Build from the single source

With the existing AgonDev toolchain:

```sh
"$AGONDEV_TOOLCHAIN/bin/ez80-none-elf-as" -march=ez80+adl -o irqcheck.o irqcheck.asm
"$AGONDEV_TOOLCHAIN/bin/ez80-none-elf-ld" -Ttext=0x40000 -e _start --oformat=binary -o irqcheck.bin irqcheck.o
```

The assembly has no includes or runtime-library dependencies. The 734-byte
binary is an ADL application loaded at `0x40000`. Identical bytes reproduced
the bug and passed after correction in two Flexe cold-boot tests. This minimal
binary has not itself been run on hardware; the earlier detailed checker
established the separate Console8 before/after evidence retained in the task.
