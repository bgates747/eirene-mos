# IRQ-001 standalone attachment preparation

Author requested a single assembly source and standalone binary, brief run
instructions, and the revised local PR draft. No publication before final approval.

IRQ-011 [x] Prepare a read-only no-argument assembly checker, with no generated
headers or runtime library. Discover the table and default handler from the
fresh-boot Eirene vector layout. Report erased defaults versus valid defaults;
never execute suspect vectors, alter tables, flash, reset or write card files.
Compile with existing AgonDev on Pi under its build FIFO (one assembler/linker
job, at most120s). Retain disassembly, source/binary hashes and build command.

IRQ-012 [x] Validate this newly built checker against the retained original and
corrected exact MOS images on Oryx using the existing qualified Flexe runtime.
Two finite cold-boot cells (one original, one fixed),60s/cell,45s no-progress,
first unexpected failure stop, normal lease/assert/owned cleanup/release.
No hardware operation. Preserve stdout/wire and runtime pins. Earlier Console8
proof remains distinct: do not imply the new checker has run on hardware.

IRQ-013 [x] Package source, binary, README and patch in a local ZIP; revise PR
first line to disclose Codex prepared it and the test suite for Brandon.
Replace the long hardware paragraph with the attached-test reproduction/fix
statement, preserving the separate hardware evidence in the task silo.
Keep the draft and attachment unpublished until final human approval.
