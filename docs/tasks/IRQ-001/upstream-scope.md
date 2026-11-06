# IRQ-001 upstream scope check — 2026-11-05

Eirene main eeebe2d34cf2941b0686d923d762378a7811b021 retains default
initialization before its BSS clear; src/init.asm allocates __2nd_jump_table in
.bss. RFC head ffab9c9 retains that ordering. The Console8 before/after proof
is retained in hardware-results.md; no new target run was performed here.

Mainstream AgonPlatform/agon-mos main8336409351ee5314e02801a7b72a4f1bb5282519
also initializes vectors before C startup, but src_startup/vectors16.asm allocates
them in the separate IVJMPTBL RAM segment. src_startup/cstartup.asm clears only
__low_bss for __len_bss. Thus the same source ordering does not imply the same bug.
Source read via GitHub API at this revision; this is not a new stock hardware test.

A retained ZDS build map, /Agon/mystuff/agon-mos/build/uart0-balls/run005/MOS.map,
corroborates the separation for that historical modified ZDS build:
BSS starts0xBC3BF, length0xAF5 (end-exclusive0xBCEB4); IVJMPTBL is
0xBCEB4..0xBCF73, length0xC0. This map is not presented as a fresh stock build.

The upstream open-issue/PR listing contained only PR1 and PR2 when checked.
No new report was published. upstream-report-draft.md is a local review draft;
fix.diff and the raw before/after reports remain in this task silo.
