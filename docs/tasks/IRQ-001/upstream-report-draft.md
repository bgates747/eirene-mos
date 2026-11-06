Codex prepared this PR and test suite on behalf of Brandon.

Eirene initializes its 48-entry RAM interrupt jump table, then clears BSS,
which contains that table. Normal startup reinstalls UART0, VBlank and I2C,
masking the loss of the other 45 defaults. This can break code that expects an
unused vector to contain the default handler, including UART1 admission.

Move the existing `__init_default_vectors` call after BSS clearing. This adds
no instructions or RAM and leaves the table layout and interrupt handlers
unchanged.

Mainstream ZDS II MOS keeps the table outside BSS and is not affected by this 
particular defect.

The attached test reproduces the problem and proves that the patch fixes it.
The ZIP contains a standalone assembly source, its binary, brief instructions
and the proposed patch. Run the same `irqcheck` binary before and after the fix.

[Download the test ZIP](https://github.com/bgates747/eirene-mos/raw/84462dd44fb78b2c99c655b2a3a964f9711875fa/irq-startup-test.zip).

```diff
diff --git a/src/init.asm b/src/init.asm
index 1647aac..84b3440 100644
--- a/src/init.asm
+++ b/src/init.asm
@@ -122,9 +122,6 @@ __init:
 		dec a			; Otherwise set to 0
 	1:	push af 		; Stack AF, will store later as __c_startup clears globals area
 
-		; Initialize the interrupt vector table
-		call __init_default_vectors
-
 		; Set rising edge triggered interrupt for vblank GPIO
 		ld	a, GPIOMODE_INTRE
 		ld	b, 2
@@ -143,6 +140,9 @@ __init:
 		ld (hl), 0
 		call ldir_handle_zerolen
 
+		; The RAM interrupt jump table is in BSS: initialize it after clearing.
+		call __init_default_vectors
+
 		pop af			; Pop the hardReset value
 		ld (_hardReset), a	; And store
 
```
