# IRQ-001: Console8 confirms the defect and correction

The real Console8 reproduced the startup bug in the original firmware and
passed with the correction. Both cold boot and the controlled software reset
show the same before/after difference. The remaining planned hardware gate is
complete; nothing is missing from the seven expected logged runs.

| Report | Installed image / path | Result |
| --- | --- | --- |
| before/I0060 | Original RC2, cold boot | 45 defaults erased; 3 normal handlers correct |
| before/I0061 | Original RC2, warm reset after table poisoning | Same 45 defaults erased |
| after/I0062 | Fixed, cold boot | All 48 correct; 48/48 install/restore pairs |
| after/I0063 | Fixed, warm reset after table poisoning | All 48 reconstructed; 48/48 pairs |
| after/R0064 | Fixed, UART regression | PASS; 8192 payload bytes verified |
| after/R0065 | Fixed, repeated UART regression | PASS; 8192 payload bytes verified |
| after/R0066 | Fixed, complete PERF2 | PASS; 9 trials, 73728 payload bytes verified |

Original ROM CRC32 is 9E08D539; fixed is DBE3E21E, both 100950 bytes. The reports
check these actual installed identities. Cold-start hardReset=1 and warm-start
hardReset=0 are recorded for each image. Every one of the 192 slot observations
was checked against the generated expected target addresses, including the
three handlers installed later by MOS. The fixed image completes 96 total
setintvector install/restore pairs. Both phase files return to 0. Counters end
before 62 and after 67, consistent with the complete prescribed sequence.

The original's expected-default predicate refuses UART1; the corrected image
accepts it. This fixture observes that predicate rather than claiming to open
an actual UART1 peripheral connection. It records invalid original entries
without executing them. The separate physical EMOS handshake failure/recovery
remains corroborating evidence of the practical consequence.

Both UART runs pass boundary lengths, zero-length refusal, BUSY/NULL callbacks,
source reuse after callback, concurrent receive processing, receiver comparison,
ordinary output before/after use and normal completion. All 90112 payload bytes
across functional/performance runs compare correctly. All 9 performance work
checksums, callback counts, independent-clock checks and receiver comparisons
pass; no pacing deadlines were missed. The journal contains exactly the expected
START/PASS pair for each of R0064..R0066, with no failures or extra attempts.

The standalone example does not create a report. Its completion rests on the
Author's overall completion report, separately from the seven logged results.
Stock Bistromathics VDP 2.16.0 is the prescribed protocol; its identity was not
independently fingerprinted in these reports. The deployed example/firmware/app
binaries still match their qualified hashes. Default-slot/API checks are not
peripheral interrupt stress; no physical logic-analyzer capture is claimed.

## Performance retained

| Scenario, median of 3 | Payload kB/s (decimal) | Calculation rate retained |
| --- | ---: | ---: |
| Bulk, no calculation requested |106.257|Not measured in this scenario|
| Paced sending plus calculation |44.076|86.080%|
| Bulk sending plus calculation |106.246|85.987%|

The calculation figures compare the same checked work loop during sending with
its own no-traffic calibration. Sending therefore costs approximately 14% of
foreground calculation capacity in the two work scenarios. These are overlap
measurements, not direct exclusive CPU-cycle profiling. The bulk-only scenario
deliberately requests no calculation; its zero work count is not 100% CPU use.

Compared with the earlier TRIM report R0059, bulk-plus-work throughput is identical
to displayed precision, paced work differs by +0.0023%, and bulk work by -0.0011%.
Those tiny differences do not establish any speed change. This was not a newly
matched timing A/B of the two startup images; it is a regression check against
retained evidence. The source correction moves one call at startup and leaves
the sender/measurement core unchanged. No firmware-size increase was introduced.

## Preserved evidence and status

The returned card is label AGONC8, vfat UUID8658-1C23. All 34 files were copied
without card writes; each archive member was compared against the captured
manifest. The complete archive and files are checksum-verified on Pi and Oryx:
`build/tm001/irq001-hardware001/returned.tar.gz`, SHA256
`d99eae263c7ebe007c41e453494eb0f007c246a3df6d82d87212367a77531aef`.
All deployed immutable inputs remain unchanged; only expected counters, phase
files and new reports/journal entries differ. No root startup, firmware image,
other card directory or file was changed during inspection.

[Raw reports](hardware-reports/), [analysis](hardware.json),
[archive receipt](hardware-receipt.json) and
[reproducible validator](../../../experiments/irq-startup/inspect_hardware.py)
are retained in this task. The card remains mounted; no firmware flash, reset,
remount or new test was performed by the agent. The last logged installed MOS
is the fixed image, consistent with the dedicated-test protocol; subsequent
physical state is not independently captured.

We now have matching source, linked-image, two-engine model and exact-image
Console8 before/after evidence, plus independent physical EMOS corroboration.
This supports the conclusion that the correction is required and fixes the
identified initialization-order defect. Main, published RC1/RC2 tags/assets and
upstream remain untouched. An upstream report or release change can now be
prepared from this evidence when requested.

Extender subsequently reported two RC2 functional runs and the original C
example passing on its corrected physical EMOS in Olimex Legacy mode. Its
separate results are [recorded by that owner](/Agon/mystuff/agon-extender/docs/tasks/EMOS-001/TEST-REUSE-RESULTS-R01.md).
Those runs are not added to the Console8 totals; its PERF2/full-pair campaign
remains outside that bounded tranche.
