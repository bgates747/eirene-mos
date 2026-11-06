# Buffered keyboard event RFC checks

`kcheck.bin` links an exact copy of the selected `src/keyboard_buffer.asm` into
application RAM. It checks the real assembly/C boundary, not a rewritten ring
model. It needs no custom firmware or keyboard input and does not modify the
installed MOS keyboard vector. A compiled binary is not an executed test.
Run by typing `kcheck` in its directory. Expected original proposal: failure at
the first wrapped dequeue (removal32). Expected corrected version: PASS after
ordering/full/empty/field/filter/clear/IFF checks. Neither expectation is yet a
recorded target outcome. No indefinite keydown test is attempted without first
passing the wrap check and pre-enqueueing a down event. No target run selected.

The unit fixture doesn't prove real UART interrupt arrival, callback coexistence,
or the installed62h dispatch. For that integration test, use Tom's supplied
examples/mos_api_pollkeyboardevent.asm with the matched MOS candidate. Its API
is A=62h, DE=address of four writable bytes, RST.LIL08h; A=0 means empty, A=1
means copied event. Fields: ASCII, modifiers, FabGL virtual key, isdown (0up/1down).
BC/DE/HL are preserved. The event array remains unchanged on empty. Poll from one
foreground consumer; `kbuf_wait_keydown` needs interrupts enabled if waiting for
future physical input. Queue both down/up/repeats in arrival order;31 usable
records, drop NEW events when full. No overflow-reporting ABI is proposed.

For a later manual integration run: record exact MOS identity, cold boot to a
normal CLI, launch the example normally; tap/release keys and modifiers while
output is busy, inspect ordered up/down events, then quit withq. Run again and
check no stale events survive normal launch/return. Check ordinary MOS editing,
keymap/sysvars and an existing keyboard-callback app still work. Deliberately
fill a queue with synthetic local unit events to test overflow; a human typing
burst alone is not an exact capacity/order oracle. A brief physical keypress
before MOS receives its UART packet, or while UART reception is blocked, cannot
be recovered by this queue. Existing getkey/state-polling programs keep their
old behavior; applications opt in to62h.

Do not replace RC3 or flash a keyboard build as an implicit step. This proposal's
base already includes the merged PR3 startup fix but not the separate async
UART proposal. Combining those is a separately qualified firmware composition.

Prepare a frozen fixture with the original ring (from a separate checkout of
241ffba) or corrected ring, then compile under the normal compiler reservation:

```sh
/Agon/mystuff/agon-dev-env/.venv/bin/python experiments/keyboard-events/prepare.py \
  --ring /absolute/selected/src/keyboard_buffer.asm --out /absolute/new/fixture
make -C /absolute/new/fixture AGONDEV_TOOLCHAIN=/your/compatible/agondev
```

The generator records source hashes and refuses an existing output directory.
`check_linked.py BINARY MAP original|corrected` checks the actual linked dequeue
return tail for all32 indices. It is a bounded static instruction-property
check, not execution of the native self-test, interrupts, or installed syscall.
The original/corrected prepared programs both require a real target run next.
