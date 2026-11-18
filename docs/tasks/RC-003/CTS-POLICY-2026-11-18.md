# UART0 CTS behavior and the FSIM P084 scope decision

**November 18, 2026. Brandon's decision is to leave MOS Eirene and EMOS
unchanged.** FSIM's instruction to avoid spinning in wait loops applies to
FSIM's own eZ80 application and its application code running under VDPlet.
The intended change is to make those two sides resume their work
asynchronously when data, credit, or completion arrives. Treating that
instruction as a requirement to remove waits inside core firmware expanded
the scope. The experimental EMOS CTS patch is therefore outside the FSIM
change and is not a requirement for it. Retain it as technical evidence.

## Why RC3 retained the CTS wait

RC-003 adopted Tom Morton's async UART0 sender from RFC revision
`ffab9c9c84a31535d1ec976b7e6f23b2579ecb80`, with the separate startup table
fix. RC3 release `3.1.0_uart0_rc_3` is pinned to
`97311c437093e416342a6c836cf9914f2ced027d`. The task deliberately kept the
RFC's CTS behavior. RC1.1 and RC2.1 remain separate startup fixes for the
earlier sender interfaces. [RC-003 adoption plan](README.md) ·
[RC3 release](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_3)

Brandon's original RFC response weighed the simpler code, potentially lower
cost on the usual path, adherence to CTS, and smaller code size. The reported
175 versus 286 assembled bytes compared the complete RFC and RC2 changes.
It did not isolate the cost of the CTS policy. The review found no statement
from Tom identifying short or rare CTS waits as his reason, and no physical
measurement of how often the original sender blocked on CTS or for how long.
The roughly 82% CPU-free figure reports useful loop throughput over a
benchmark window. It does not bound a single interrupt pause.
[Original RFC discussion](https://github.com/AgonPlatform/eirene-mos/pull/2#issuecomment-6671106882)

## What the source establishes

- Upstream Eirene main at `3a7259c58bfa6f34f58afe24087f418cef0148e0` has
  synchronous UART0 output with a CTS wait in the foreground send path.
  The async syscall and its wait inside the TX interrupt are in the open
  RFC. [Eirene main](https://github.com/AgonPlatform/eirene-mos/tree/3a7259c58bfa6f34f58afe24087f418cef0148e0) ·
  [Async UART0 RFC](https://github.com/AgonPlatform/eirene-mos/pull/2)
- Fork RC3 and production EMOS v0.3.0 with guarded RFC25 use the RFC's
  interrupt-driven refills of up to 16 bytes. Before each refill, including
  the last, the handler waits on active-low CTS with interrupts disabled.
  If the VDP holds CTS inactive, foreground execution, incoming UART
  service, and timer and VBlank interrupts wait too. The async call can
  return quickly while a later refill delays those services. The guarded
  EMOS API has different admission semantics from bare RC3.
  [RC3 release notes](rc3-release-notes.md) ·
  [EMOS production source](https://github.com/bgates747/agon-emos/blob/abefa2f943eb3089c08d85bf39e48ebb4938f4bd/src/emos_uart0_rfc25_io.asm)
- Optional EMOS patch `44f791aa706d9a28c083d81714926735cb922c90` checks CTS
  before advancing the source pointer or count. When blocked it parks the
  pending transfer, masks the TX interrupt, arms the modem-status interrupt,
  acknowledges status, resamples CTS, and returns. A modem event or VBlank
  rearms the existing TX copier. The parked buffer stays borrowed, including
  if CTS never clears. The callback releases the buffer after its last FIFO
  fill. UART wire drain and the VDP reply are later, distinct events.
  The existing `BUSY` result also covers a modem interrupt enable already
  owned by another operation. [Exact optional patch](https://github.com/bgates747/agon-emos/commit/44f791aa706d9a28c083d81714926735cb922c90)
- The Extender build report records the disabled ROM as byte-identical to
  production. The enabled build adds 118 ROM bytes and one BSS byte and
  passed 90 linked model cases. Those checks cover blocked refills, rearming,
  and ownership in the model. The exact P084 candidate had no hardware result
  in this review. [P084 build report](https://github.com/bgates747/agon-extender/blob/49a936e0ec39f13550b25fbc5c2951cceb5a9441/docs/tasks/NET-004/P084-UART0-CTS-PORT.md)

## Observed results and their limits

The RC3 Flexe latency suite recorded 16 receive overruns in the interpreter
cell and zero in the JIT cell. With the VSync workload, the longest timer
service gaps were 12,935 and 43,648 model ticks in the two async cells,
compared with 73 ticks in the synchronous cells. Those are service gaps in
the model. They do not time individual CTS waits or establish a hardware
failure. [RC3 latency results](../RFC-001/latency-findings.md)

A MechAgon hardware run, actual108, did record a UART0 receive overrun.
That experimental ROM already deferred on blocked CTS, so the overrun cannot
be attributed to the original spin. A separate older CTS-edge EMOS trial,
actual159, recorded a shorter mean submit-to-source observation than
actual158 (0.057 versus 16.640 nominal ms). The VBlank-derived clock was
coarse and the ROM/profile differed from P084. That comparison supports
investigating how promptly the sender resumes. It does not measure physical
CTS incidence, CTS wait duration, or P084's effect.
[Actual108 source review](https://github.com/bgates747/agon-mos/blob/6fbd1be/docs/handoffs/mechagon-actual108-uart0-source-return-2026-11-07.txt) ·
[Earlier CTS-edge hardware report](https://github.com/bgates747/agon-extender/blob/49a936e0ec39f13550b25fbc5c2951cceb5a9441/docs/tasks/NET-004/UART0-CTS-PROGRESS-R01-RESULT.md)

The source explains how backpressure can delay interrupt service. The review
found no hardware error traced to that wait in current Eirene or production
EMOS. The initial review recommended retaining P084 as an optional candidate
for qualification. Under Brandon's scope decision, that qualification is
separate from FSIM and would require a separate decision. A matched test,
if selected, could record CTS pause frequency and duration, input/RX/timer
progress during the pause, and exact bytes and one callback when transmission
resumes.
