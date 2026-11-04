IRQ-001: INTERRUPT DEFAULTS BEFORE/AFTER
Directory: /test/mos-uart0
Use stock Bistromathics VDP 2.16.0. Included if needed:
  flash vdp vdp-stock.bin
Keep the normal flash updater checks. Let it finish/reset as instructed.

A. From /test/mos-uart0:
  flash mos mos-before.bin
After the updater finishes, power off/on once and wait for the MOS prompt.
  cd /test/mos-uart0/before
  irqcheck
Expect IRQ ORIGINAL REPRODUCED: 45 erased default entries.
The app saves I0060.log, poisons the table under DI and software-resets ONCE.
After normal boot, WITHOUT pressing reset/power cycling, return here:
  cd /test/mos-uart0/before
  irqcheck
Expect IRQ ORIGINAL REPRODUCED again, then IRQ COLD/WARM PAIR COMPLETE.
This records the bug without jumping through an invalid handler.

B. Return to /test/mos-uart0:
  flash mos mos-fixed.bin
After the updater finishes, power off/on once and wait for the MOS prompt.
  cd /test/mos-uart0/after
  irqcheck
Expect IRQ FIX PASS and VECTOR ROUNDTRIPS 48/48.
After its ONE software reset, WITHOUT another reset/power cycle:
  cd /test/mos-uart0/after
  irqcheck
Expect IRQ FIX PASS, VECTOR ROUNDTRIPS 48/48 and COLD/WARM PAIR COMPLETE.
Then, from this after directory, type each command with no switches:
  test       (require RC2 PASS)
  test       (require RC2 PASS again)
  example    (require RC2 EXAMPLE PASS; no log)
  perf       (require PERF2 PASS, all nine trials/receiver checks)

Each app should finish within two minutes; a stall or FAIL is failure.
On unexpected failure stop, keep all reports and the last progress line.
Do not proceed to a different case or reset an uncertain borrowed transfer.
Return the SD to Oryx for inspection after completion. No root startup script
is changed. Logs use sequential numbers, not the Agon's clock. Before starts at I0060/I0061; after starts at I0062/I0063.
Then after has R0064..R0066 plus runs.log for UART/performance.
Before/after counters are independent; retries keep/increment their numbers. Retrying preserves/increments the counters.
To repeat a complete startup pair, power off/on before the first invocation.

Both MOS banners still say Eirene UART0 RC2: only initialization order differs.
The probe verifies the exact installed ROM and prints its CRC32:
  BEFORE 9E08D539       FIXED DBE3E21E       both 100950 bytes
Wrong ROM is refused before any table/reset operation.
The original firmware's erased defaults are EXPECTED evidence, not a test
crash. On the fixed firmware all 48 slots must be correct on both starts.
Vector installation/restoration tests use the normal MOS API under DI;
these are table/API checks, not real peripheral interrupt stress.

Leave fixed MOS installed for dedicated testing if desired. Restore when needed:
  cd /test/mos-uart0
  flash mos mos-stock.bin
Do not run this deliberate-reset fixture on a live Extender/EMOS session.
This is a private test candidate, not a replacement published RC2 or stock MOS.
