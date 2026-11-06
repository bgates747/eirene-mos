**STARTUP-FIXED RC2 REFRESH — same RC2 ABI and sender behavior.** Use this revision instead of the original RC2, which retains the inherited interrupt-table startup bug. Original tags and downloadable assets are preserved.

The only MOS source change from published RC2 is moving the existing default interrupt-table initialization after BSS clearing, as in [startup PR3](https://github.com/AgonPlatform/eirene-mos/pull/3). Only init.o changes; firmware size, sender objects, 42h/43h interface and the lean RC2 caller contract remain unchanged. This is not a migration to Tom's 25h RFC API; that separate ABI is RC3.

The MOS banner still says RC2; identify this refresh by its firmware filename and CRC below. The original target library is pinned so the startup fix brings no unrelated SDK changes.

The ZIP includes complete matching MOS source/binary/map/ELF, functional fixture and worked-example sources/binaries, standalone startup checker, frozen target SDK library/headers, build/use how-tos, raw evidence, licenses/credits and checksums. Run irqcheck, test and example by name with no switches. No modified VDP is required.

Fresh Flexe/JIT startup, UART regression and worked example pass, verifying 8192 payload bytes with no backend/UART errors. The exact corrected RC2 ROM matches the earlier Console8-qualified startup-fixed image byte for byte. Matching regenerated apps were tested in Flexe here. No new throughput/CPU claim is made. Main and original release tags/assets remain unchanged.

Source/tag: `b219486068b41af8a760f7e4c6b132eea43377b1` / `3.1.0_uart0_rc_2.1`. MOS CRC32 `DBE3E21E`, 100950 bytes. MOS SHA256 `4550f60e74bb7be7d99e4fd1acaddaf9ac43d5b02a242fadee60c6e92aec30dc`.
