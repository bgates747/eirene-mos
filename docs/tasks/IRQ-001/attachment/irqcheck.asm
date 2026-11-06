; Read-only Eirene MOS interrupt-default regression check.
; Prepared by Codex for Brandon. SPDX-License-Identifier: MIT
; AgonDev GNU assembler; no includes, generated symbols or runtime libraries.
; Run immediately after boot, before installing custom IRQ/RST handlers.
.assume adl=1
.text
.global _start
_start:
 jp start
 .balign 64
 .ascii "MOS"
 .byte 0,1
start:
 push ix
 push iy
 ; Eirene's IM2 table is at ROM 0100h. Follow its first ROM JP to
 ; locate the RAM table, so relinking MOS requires no address edits.
 ld a,i
 cp 1
 jp nz,unsupported
 ld hl,0
 ld a,(0x100)
 ld l,a
 ld a,(0x101)
 ld h,a
 ld a,(hl)
 cp 0xc3
 jp nz,unsupported
 inc hl
 ld hl,(hl)
 call ram_address
 jp c,unsupported
 ld (table),hl
 ld de,191
 add hl,de
 call ram_address
 jp c,unsupported
 ; After fresh boot RST20's RAM JP names the default IRQ handler.
 ; Decode that target, checking the unmodified EI/RETI.L signature.
 ld a,(0x20)
 cp 0xc3
 jp nz,unsupported
 ld hl,(0x21)
 call ram_address
 jp c,unsupported
 ld a,(hl)
 cp 0xc3
 jp nz,unsupported
 inc hl
 ld hl,(hl)
 push hl
 ld de,0x20000-4
 or a
 sbc hl,de
 pop hl
 jp nc,unsupported
 ld (default_handler),hl
 ld a,(hl)
 cp 0xfb
 jp nz,unsupported
 inc hl
 ld a,(hl)
 cp 0x5b
 jp nz,unsupported
 inc hl
 ld a,(hl)
 cp 0xed
 jp nz,unsupported
 inc hl
 ld a,(hl)
 cp 0x4d
 jp nz,unsupported
 ; Inspect all 48 RAM entries. Never execute them or change them.
 ld ix,(table)
 ld b,48
 ld c,0
 xor a
 ld (erased),a
 ld (bad),a
 ld (active_bad),a
slot:
 ld a,(ix+0)
 or (ix+1)
 or (ix+2)
 or (ix+3)
 jr nz,not_erased
 ld hl,erased
 inc (hl)
not_erased:
 ld a,(ix+0)
 cp 0xc3
 jr nz,bad_slot
 ld hl,(ix+1)
 ld a,c
 cp 0x18/2                  ; UART0, I2C and VBlank are reinstalled by main.
 jr z,active_slot
 cp 0x1c/2
 jr z,active_slot
 cp 0x32/2
 jr z,active_slot
 ld de,(default_handler)
 or a
 sbc hl,de
 jr z,next_slot
 jr bad_slot
active_slot:
 ; All three installed handlers must still point into firmware ROM.
 ld de,0
 or a
 sbc hl,de
 jr z,bad_slot
 ld de,0x20000
 or a
 sbc hl,de
 jr c,next_slot
bad_slot:
 ld a,c
 cp 0x18/2
 jr z,bad_active
 cp 0x1c/2
 jr z,bad_active
 cp 0x32/2
 jr nz,count_bad
bad_active:
 ld hl,active_bad
 inc (hl)
count_bad:
 ld hl,bad
 inc (hl)
next_slot:
 lea ix,ix+4
 inc c
 djnz slot
 ld a,(active_bad)
 or a
 jr nz,failed
 ld a,(bad)
 or a
 jr z,passed
 cp 45
 jr nz,failed
 ld a,(erased)
 cp 45
 jr nz,failed
 ; Each of the 45 default entries is erased; all 3 active entries survived.
 ld hl,bug_message
 call print
 ld hl,1
 jr done
passed:
 ld hl,pass_message
 call print
 ld hl,0
 jr done
failed:
 ld hl,fail_message
 call print
 ld hl,2
 jr done
unsupported:
 ld hl,unsupported_message
 call print
 ld hl,2
done:
 pop iy
 pop ix
 ret
; Carry set unless HL lies in MOS RAM BC000h..BFFFFh.
ram_address:
 push hl
 ld de,0xbc000
 or a
 sbc hl,de
 pop hl
 ret c
 push hl
 ld de,0xc0000
 or a
 sbc hl,de
 pop hl
 ccf
 ret
; Zero-terminated text via stock character output; preserve the text pointer.
print:
 ld a,(hl)
 or a
 ret z
 push hl
 rst.lil 0x10
 pop hl
 inc hl
 jr print
pass_message:
 .asciz "IRQ PASS: 45 default entries valid; 3 active entries valid.\r\n"
bug_message:
 .asciz "IRQ BUG REPRODUCED: 45 default entries erased; 3 active entries valid.\r\n"
fail_message:
 .asciz "IRQ FAIL: unexpected table contents; check a freshly booted Eirene.\r\n"
unsupported_message:
 .asciz "IRQ UNSUPPORTED: expected fresh-boot Eirene vector layout not found.\r\n"
table: .ds 3
default_handler: .ds 3
erased: .byte 0
bad: .byte 0
active_bad: .byte 0
