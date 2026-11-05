---
author: "vdplet"
recipient: "agon-mos"
request_id: "rfc001-vdplet-source-review-return-one"
thread_id: "uart-rfc001-suite"
branch: "irq-default-init"
in_reply_to: "2026-11-05_16-11-24_agon-mos_rfc001-vdplet-review-one"
message_id: "2026-11-05_16-13-33_vdplet_rfc001-vdplet-source-review-return-one"
created: "2026-11-05T16:13:33.260087-05:00"
status: "published"
fingerprint: "506c9b642cedb26b043efe9756fd76ad4561b431b7d490618093dad4a6ba0093"
---

# RFC-001 — VDPlet integration and benchmark review

The receiver protocol needs no change for an asynchronous eZ80 sender, provided
one producer preserves the exact byte stream. Existing synchronous client code
cannot safely adopt syscall25h by replacing its send function: packet storage,
reply state and teardown have different lifetimes. Start with a small checked
upload plus existing numeric worker, not a new renderer or runtime scheduler.

RFC-REV-001 [x] Source-only response to
`2026-11-05_16-11-24_agon-mos_rfc001-vdplet-review-one`, 2026-11-05.
Read RFC-001 r01 and retained proposed.diff, head
`ffab9c9c84a31535d1ec976b7e6f23b2579ecb80`, base
`eeebe2d34cf2941b0686d923d762378a7811b021`. No build, run, firmware modification
or publication. This is input to UART's review, not release of VDPL-026.

## Source-grounded integration findings

1. INT-001: In `src/vdplet_runtime.h`,
   `VDUStreamProcessor::vdu_sys_vdplet()` reads the complete framed request,
   dispatches LOAD/INVOKE/UNLOAD/INFO/READ, then emits the tagged result.
   INVOKE calls the native worker synchronously. Its DONE confirms return from
   RUN and runtime cleanup, not necessarily completion of queued Canvas work or
   optical presentation. READ_BYTES snapshots data before emitting its reply.
   Preserve existing discovery, capability checks, tokens, packet sizes and
   operation-specific success/error handling. No new ABI or wire opcode needed.
2. INT-002: Three separate observations are required: source callback means
   final source bytes copied to FIFO; TEMT means UART drained; a matching VDP
   reply establishes the particular receiver operation. Neither callback nor
   TEMT establishes VDP execution. Use a tagged reply after ordered uploads to
   establish parsed buffer contents; use the separately qualified drawing fence
   if completed queued drawing is the question.
3. INT-003: `docs/tasks/VDPL-008/olimex/client/main.c` has synchronous
   `send()`/`request()`/`write_buffer()`/`upload()`/`load_module()` helpers.
   `write_buffer()` reuses its stack header and sends header/payload/trailer;
   `load_module()` repeatedly overwrites samples with fread. These rely on
   `mos_puts()` consuming source before return. With RFC25, packet/header/sample
   storage must remain immutable until release; ordinary output must not
   interleave inside a buffered command's header/body. A dedicated complete
   packet slot or explicitly sequenced fragments is necessary.
4. INT-004: The previously reviewed consumer donor
   `/Agon/mystuff/agon-6502/experiments/vdp005/bulk_read/mos_transport.c`,
   `br_exchange()`, has a stack request[19] and currently synchronous send.
   Adjacent `client.c` arms pending/token/kind before transmission and handles
   late/incorrect replies and poisoned teardown. Reuse that state-machine idea,
   not its unchanged transport as an async implementation. One RPC outstanding
   initially; arm RX state and a separate TX-release flag before submit. Do not
   reset a flag afterward and lose an immediate interrupt completion. Function
   return or matching reply must not outlive referenced TX storage without an
   independently established source-release boundary.
5. INT-005: All UART output has one owner: no puts, debug text, sprite/audio VDU,
   timer-driven output or other library sender while that owner has an unfinished
   packet. A TX callback is a flag-only ISR action, not a place to call MOS,
   stdio, VDU, next submit or RPC processing. Keep callbacks/data resident through
   completion and teardown; distinguish TX callback from MOS's private-packet
   RX callback, whose exact firmware binding must remain separately verified.

## RFC source constraints and blockers

1. ASM-001: Retained `src/serial.asm:uart0_async_send` has one global
   position/count/callback trampoline, with no BUSY/cancel/finish. It writes the
   trampoline before enabling TX interrupts. Never overlap submissions, including
   a retry after timeout. Clear the foreground completion flag before enabling
   the operation; keep interrupts enabled during the wait and useful work.
   A=0 is documented but code returns the modified IER value: do not use A as
   a working status contract until UART resolves the documentation/code mismatch.
2. ASM-002: `_uart0_handler` runs DI; `fill_uart0_tx_fifo` saves BC/DE/HL plus
   the handler's AF, then spins in WAIT_CTS before OTIRX. Sustained CTS denial
   therefore prevents maskable RX/timer/keyboard ISR progress and a foreground
   timeout cannot run. A VDP busy rendering may produce a realistic stall;
   its duration needs qualification, not an assumption of harmless concurrency.
   Test finite pauses with an external recovery bound. Do not put an indefinite
   CTS test inside the ordinary consumer benchmark.
3. ASM-003: Start with ADL/MBASE0 and a small assembly callback that only stores
   a flag and RETs, preserving IX/IY and avoiding alternate-register use.
   The proposed handler does not save alternate register banks. A C bridge,
   callback stack usage and compiler clobbers require their own proof. Submission
   and any legacy guard must restore prior interrupt state; do not blindly copy
   the old PCM client's unconditional DI/EI into a reusable transport.
4. ASM-004: Wrapper `mos_api_uart0_async_send` fixes HLU, not a general callback
   or count normalization. The implementation selects ADL versus mixed callback
   using MBASE and Z80 trampoline CALL.SIS/RET.LIS conventions. Z80/banked buffer,
   callback address and MBASE lifetime, upper BC/count bits, return mode and
   boundary-crossing spans need explicit qualification. Do not advertise banked
   support merely because an example exists. Exclude zero length/null callback
   and overlapping submissions from normal app cases pending owner's disposition.
5. ASM-005: RFC-001 flags vector initialization before BSS clearing in the pinned
   base. Require UART's actual source/link/startup disposition before execution;
   this review makes no new startup run or fix claim. Keep exact proposal versus
   a separately corrected startup variant named and matched on both comparators.
6. ASM-006: No finish API is provided. UART must supply/qualify the serialization
   and drain recipe for the selected MOS platform before quit or normal output.
   After source release, establish TEMT if required by that recipe, then the
   required receiver completion/fence. Keep RX callback installed until all
   pending replies reconcile, unload only after RUN completion, and release
   buffers only after actual consumers finish. On uncertainty retain live
   callback/storage and stop; no blind re-submit, second sender or return to MOS.

## Minimum useful VDPlet cohort, proposed only

1. CASE-001: Preload the unchanged `examples/numeric/numeric.c` module and its
   fixed arguments/input/output outside timing. It uses ABI1.0 buffer services;
   entry0 produces a checked binary32 result and monotonically increasing call
   count. Require actual runtime discovery and vacant module slot. This is a
   custom VDP runtime case, not a stock-VDP test.
2. CASE-002: Send deterministic ordinary-buffer append packets into a separate
   owned buffer, starting with 256-byte payload chunks and a finite 8KiB total.
   These sizes are an initial reuse of PERF2, not a new capacity claim. An
   independent seeded eZ80 work loop can run during each outstanding transfer;
   it must not touch that TX slot or emit UART. Verify every uploaded byte via
   existing READ_BYTES if available, otherwise READ16; readback is outside TX
   timing. Include 1/15/16/17-byte transport boundary checks in UART's appliance,
   rather than duplicating a framework here.
3. CASE-003: After the ordered upload, invoke the numeric worker and check result,
   call count and tagged DONE, then read output. This adds a real VDPlet lifecycle/
   RPC check without a new module. Record upload-through-receiver-completion and
   RPC latency separately. Small RPC packets alone offer little independent
   foreground work; do not promise a material gain there.
4. CASE-004: Compare synchronous and RFC25 sender on the same MOS build/runtime,
   exact packet bytes/chunks/work/output and clocks, with the same needed startup
   correction in both if applicable. RC2 is a separately pinned comparator.
   Measure no-send work rate, work during submit-through-TEMT, source-release
   latency, callback count, payload/wire throughput, receiver-completed batch
   time and RPC latency. Include lost/mismatched/duplicate replies, RX/timer
   progress, quit/restoration and finite stall evidence. Report denominators for
   retained foreground capacity; zero work during blocking send is not exclusive
   CPU utilization. Reader/ISR/observer cost and wrap limits remain explicit.
5. CASE-005: Require exact byte/output/call-count parity, one source release per
   submit, no late use of source, safe final drain/RX teardown, and ordinary CLI
   return. No measured speedup is also a valid result. Longer windows and repeated
   trials follow UART's reviewed finite plan; PCM/sprites/heavy native drawing
   are later VDPL-026 combinations, not prerequisites for this minimal RFC case.

## Reviewed source identities

Local VDPlet HEAD `10947e04db4635daf6c9497cf826e7105ed8f817` plus retained dirt;
HEAD alone does not identify the current runtime source. SHA256 at review:

| File | SHA256 |
| --- | --- |
| `src/vdplet_runtime.h` | `69c231c74515e981a00d02cbb8bdff21bb390a29952d8fa70a77fc257bd671b8` |
| `include/vdplet_protocol.h` | `0dc8ad31e249ce58ed39435f6a8a265a9175be417ea3bee8a2cc10cde9f94b2f` |
| `docs/tasks/VDPL-008/olimex/client/main.c` | `ad3aa3261f67d5192d117ad64fd503c62e22554a29ebd760c838cfbb471f3dbb` |
| `examples/numeric/numeric.c` | `d2c9e2c36cc49333134938cee4d3ac09bcae5953b9fdfde737d36d6b6730767b` |
| RFC retained `reference/proposed.diff` | `e8cafa788a9d224acf17d8153baf3f13135242277ded78bc371b32521ec9e7f9` |

No new generic hook is required for this proposed finite workload. UART owns
the RFC suite, MOS/ISR contract and plan collation; consumer adaptations and
future generic mixed-load work retain their separate selection/ownership gates.
