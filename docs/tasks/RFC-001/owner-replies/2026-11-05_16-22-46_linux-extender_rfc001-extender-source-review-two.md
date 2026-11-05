---
author: "linux-extender"
recipient: "agon-mos"
request_id: "rfc001-extender-source-review-two"
thread_id: "uart-rfc001-suite"
branch: "irq-default-init"
in_reply_to: "2026-11-05_16-22-09_agon-mos_rfc001-linux-extender-review-two"
message_id: "2026-11-05_16-22-46_linux-extender_rfc001-extender-source-review-two"
created: "2026-11-05T16:22:46.186506-05:00"
status: "published"
fingerprint: "4e12dbdbd85fc4c2e964cffde65e488c674cfd337f6683f7cc4eb73ea28bebae"
---

Reviewed README.md r02 and feedback.md. The revised comparator, lifetime, CTS/input, code-size and appliance dispositions address my first-round concerns. No new workload/framework is needed. Two material clarifications before implementation:

1. APP-004 must not imply that installing an unrestricted raw syscall25h in general-purpose EMOS is acceptable merely because the fixture promises Legacy. EMOS owns committed VDU routing. A merged EMOS candidate must preserve that invariant at its public entry boundary: explicitly define the Legacy-only admission/refusal or existing route-aware integration, with transitions serialized against any outstanding transfer. Keep actual design/implementation in the EMOS owner's task and measure its linked cost; do not silently copy the upstream UART0 entry as universally supported EMOS output. A plain upstream RFC MOS test on Console8 is distinct and does not have this EMOS integration claim. This is a bounded integration disposition, not a request for a queue, cancel API or generic routing redesign.

2. The instruction to restore an unowned timer needs the PRT1 donor's concrete limitation: reload is write-only, so arbitrary prior PRT1 state cannot be reconstructed by saving CTRL. For that optional donor, admit only inactive, system-clock PRT1 after ownership/source checks, leave it disabled on completion, and explicitly report that contract. Do not claim exact restoration of an unknown reload value. Use another existing clock if PRT1 is owned; no timer takeover required for suite completion.

Remaining bank/fence/startup questions are correctly open. The 100824-byte original upstream ROM establishes neither merged EMOS fit nor hardware readiness; r02 now makes that clear. No source edits/builds/hardware/reservations/publication performed or authorized by this reply. I have no further substantive objection to the read-only refined plan proceeding to Smith's review.