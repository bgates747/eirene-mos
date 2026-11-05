Tom, Codex compared this with our experimental [Eirene MOS 3.1.0 UART0 RC2](https://github.com/bgates747/eirene-mos/releases/tag/3.1.0_uart0_rc_2) sender. I include its full comments below for the benefit of other reviewers to know other options on the table:

Both proposals use UART interrupts and up-to-16-byte OTIRX refills, accept one borrowed buffer at a time, and leave ordinary RST18 behavior unchanged. The main differences are:

- Yours integrates TX handling directly into MOS’s existing UART handler. Ours temporarily installs a replacement handler and restores the original afterward. Your integration is simpler.
- Yours waits for CTS inside the interrupt handler, with interrupts disabled. Ours defers transmission when CTS blocks and uses a modem-status interrupt to resume, allowing other interrupts and foreground work to continue meanwhile.
- Yours provides one submission syscall. Ours also provides a nonblocking finish call that checks the transmitter has drained and restores the original handler.
- Ours rejects zero-length and overlapping submissions, returns explicit status values, and permits a null callback. Yours leaves those responsibilities with the caller.
- Yours includes a classic Z80 callback path. Ours requires ADL mode with MBASE zero.
- In the retained builds, your changes add 175 assembled code bytes and 11 bytes of state. Our RC2 adds 286 code bytes and 9 bytes of state.

In both implementations, the callback means the source bytes have entered the FIFO, not that the UART has drained or the VDP has finished processing them.

The human comments resume here. The main thing that jumped out at me was that yours waits for CTS inside the interrupt handler with interrupts disabled. I liked that Codex’s solution leaves the interrupt handler when CTS blocks, letting the application continue useful work while MOS handles resuming transmission. Codex liked it too, obviously, but pointed out that your way is simpler, the common path may be cheaper, it intrinsically obeys flow control, and is probably entrely adequate for a hobby machine. I am personally leaning toward your more economical approach at this point.

Approve of non-ADL support. Totally fine for making callers more responsible for their own bookkeeping than our version does, especially since it reduces the number of bytes added. Overall very happy with how this is shaping up, thanks for putting me on to it in the first place and submitting this candidate. I hope we get merged. - Brandon
