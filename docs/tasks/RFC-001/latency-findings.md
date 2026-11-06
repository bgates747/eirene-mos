# RC3 responsiveness: transfer passes, receive loss in one model cell

The new test found a concrete tradeoff worth checking on Console8 before using
CPU savings alone to judge the sender. While the VDP waits to display a frame,
Tom's sender can wait for CTS inside its interrupt. That can delay other timer
and incoming-data service. One Flexe engine reported incoming bytes dropped;
the other did not. This is a model finding, not proof of a Console8 failure.
The successful Jukebox listening result on RC3/VDPlet remains valid for that
workload; this test does not relabel it or establish a playback regression.

## Exact result

Oryx generation326, released with fresh empty-host evidence. Two cells ran,
using unchanged published RC3 B08C80B8/d7a51147 and the identified diagnostic
actual-firmware VDP from RC-003, not a stock VDP binary. No physical action,
new sender variant or upstream notification occurred. Runner stopped on the
first failing host check after the interpreter cell; no replay or extra cell.

| Model engine | Complete upload payload checked on wire | Key packets emitted / latched during windows | RX overruns | Disposition |
| --- | ---: | ---: | ---: | --- |
| JIT |622592 bytes|32 /32|0|Selected functional checks pass|
| Interpreter |491520 bytes|32 /30|16|Host qualification fails|

Both guests completed all8 sync/async cases, exactly matched all136 outbound
packets, observed68 expected async callbacks in total, checked all bytes of the
last8KiB receiver buffer after each case, restored disabled timer source/control
and vector state and null keyboard callback, then returned to the CLI. Backend
failure/unhandled/unregistered/unmapped counters and TX drops were zero.
The host's16 RX overruns are decisive receive-loss evidence in that MODEL.
The keyboard callback counts only inside the measurement windows:32 versus30
alone does not prove exactly two complete key packets were permanently lost,
or exclude delayed events arriving after a window. All32 A key packets are
present in the captured VDP-to-MOS stream; this is not a missing-injection case.

The guest's `LAT CASE PASS`/`RC3 LATENCY PASS` means its byte/callback/restoration
checks completed, not that input retention or responsiveness was certified.
It cannot read the host's UART-overrun counter. Do not accept guest PASS alone.

## What the instrument shows and what it does not

A polling72kHz PRT1 clock avoids depending on serviced wrap interrupts during
finite CTS waits. Separate nominal1ms PRT2 service maximum gaps stayed73 ticks
in all synchronous cells. With8 VSync waits the async maximum was12935 ticks
in JIT and43648 in interpreter. These are model-counter observations, not
hardware milliseconds or estimates of real CPU cost. The engines' very different
VDP-to-CPU pacing is visible in their VBlank counts and prevents treating either
as a calibrated physical latency result. Individual measured gaps stayed below
the65536-tick clock-wrap ambiguity bound; unbounded stalls are not measurable.

Synchronous foreground work cannot run during its blocking call, although its
interrupts can remain serviced. Async foreground work runs between refills, but
its CTS wait can stall interrupts. A tiny measured key age in the async case
starts only when MOS finally delivers the callback; it excludes preceding wire/
FIFO/ISR delay and must not be reported as end-to-end key latency. Coalesced
foreground observations remain counted by the interrupt latch.

Source review provides a plausible mechanism: exact RFC `WAIT_CTS` in
`src/serial.asm` spins on PD_DR bit3 while the UART ISR is under DI. This delays
its own receive service as well as PRT/VBlank. The source establishes that
possibility; this campaign alone does not establish which hardware workloads
would overflow, nor exclude model scheduling contributions. No firmware fix is
selected on this evidence. Ask Flexe for source-only model interpretation and
use the finite fixture for a separately selected manual Console8 confirmation.

## Reproduction and next work

Task: [second-tranche.md](second-tranche.md). Source:
`experiments/uart0-rfc-latency`; frozen build `build/rfc001/lat001-build02`.
App22949 bytes, SHA256
`17e74eea2dc0deaf16ab042a7ca1dc87802f827410336ce126535730871dad46`.
Pinned SDK library matches RC3's original distribution. Clean build with
-Wall/-Wextra/-Werror passed under Pi compiler205, which was released and actual
next-owner Flexe notified. Assembly disassembly/map and source hashes retained.

[latency-results.json](latency-results.json) contains actual row/counter data;
[latency-model-reports](latency-model-reports) retains reports/actions/counters.
`build/rfc001/lat001-evidence.tar.gz` (SHA256
`f5d7280f48b924222d2c686a87cd5ef3a1e39d9fadfb687cce8c53bade1be8c9`)
contains stopped private cards, actual streams/runtime links, actions, stats and
runner output. Local extracted reports/wire proofs supplement that immutable
archive; interpreter report is recoverable from its included FAT image. No
shared runtime/helper was edited; verified Jukebox PS/2 shim was copied unchanged.

Remaining work: confirm actual hardware service gaps/receive behavior before
calling the latency cohort qualified; then complete the already planned matched
CPU/throughput fixture. PER-001/PER-002 remain unimplemented, not completed by
these transfer results. No permanent-stall test or additional MOS robustness
code is proposed. Keep RC3 private and experimental pending the RFC merge.
