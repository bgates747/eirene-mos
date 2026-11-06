**STARTUP-FIXED RC1 REFRESH — same RC1 ABI and sender behavior.** Use this revision instead of the original RC1, which retains the inherited interrupt-table startup bug. Original tags and downloadable assets are preserved.

The only MOS source change from published RC1 is moving the existing default interrupt-table initialization after BSS clearing, as in [startup PR3](https://github.com/AgonPlatform/eirene-mos/pull/3). Only init.o changes; firmware size, sender objects, 42h/43h interface and the guarded RC1 caller contract remain unchanged. This is not a migration to Tom's 25h RFC API; that separate ABI is RC3.

The MOS banner still says RC1; identify this refresh by its firmware filename and CRC below. The original target library is pinned so the startup fix brings no unrelated SDK changes.

The ZIP includes complete matching MOS source/binary/map/ELF, functional fixture and worked-example sources/binaries, standalone startup checker, frozen target SDK library/headers, build/use how-tos, raw evidence, licenses/credits and checksums. Run irqcheck, test and example by name with no switches. No modified VDP is required.

Fresh Flexe/JIT startup, UART regression and worked example pass, verifying 8192 payload bytes with no backend/UART errors. The exact new RC1.1 image passed the model checks below; no new physical run is claimed. Original RC1 hardware evidence describes the unchanged sender, not this new image. No new throughput/CPU claim is made. Main and original release tags/assets remain unchanged.

Source/tag: `d268d0b344dde678250ef692986c7d8bf79f7c4b` / `3.1.0_uart0_rc_1.1`. MOS CRC32 `97ADC5DB`, 101140 bytes. MOS SHA256 `2825c2830600128a3c93fa78fdb787b3fb7e831c80b862a3adf9164b1b4a8792`.
