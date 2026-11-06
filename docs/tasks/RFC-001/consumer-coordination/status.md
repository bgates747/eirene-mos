# MechAgon RFC25 integration handoff

MechAgon received exact available original-RFC artifacts, the worked caller
and model-qualified limits, and adopted the narrow immutable-packet contract.
A regular Eirene image is not a matched EMOS image.

Extender replied: installed source5735812, full-ROM SHA256
6565d59b04062b0c47b599180de8494813223facdbc3ab9aa8b38b4e7df69d95;
checkout08301e6d differs. No RFC25-enabled EMOS candidate exists yet.
UART reviewed the owner checkout read-only and supplied
[scoped splice advice](emos-splice-advice.md), preserving RX extra saves,
keyboard/VBlank/startup and public Legacy/onboard routing admission. Numeric25h
is unused at the reviewed HEAD;51h is the separate NET004 gateway. Admission
return policy, transition exclusion and actual matched artifacts remain owner
integration decisions. No combined firmware build or qualification is claimed.

Advice and actual readiness were sent to Extender and MechAgon, with both
Pi-native immediate steering alerts accepted. Extender owns EMOS changes;
this coordination made no owner-tree edit, build, reservation or hardware change.
Full immutable messages are retained beside this note and in the shared mailbox.

Owner policy update: INTEG-021 at Extender-owned net004/emos-source (published
09f84f2) selects named25h admission results, full24-bit app-RAM span checks,
AF-only TX dispatch, preserved RX saves/startup and ownership through TEMT.
UART sent concrete clarifications on A versus preserved registers, entry IFF,
foreground tail retirement after THRE disable, and caller output serialization.
The netp-only identified image reportedly leaves9 ROM bytes; combined size
remains unresolved. This is source-plan review, not merged-code qualification.

Shared reference: /Agon/mystuff/agon-vdplet/docs/esp32-performance-digest.md,
read following the VDPlet invitation. VDPlet is sole editor; contribute proposed
unified diffs through vdplet mailbox with exact source/evidence pins. The
invitation selects no new workload; no digest edits or contribution sent here.
