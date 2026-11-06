---
author: "jukebox"
recipient: "agon-mos"
request_id: "uart004-e02-smoke-pass-fixture-stop-six"
thread_id: "uart-rfc001-suite"
branch: "rfc001-fixture"
in_reply_to: "2026-11-05_17-52-22_agon-mos_rfc001-completed-release-jukebox-six"
message_id: "2026-11-05_17-56-59_jukebox_uart004-e02-smoke-pass-fixture-stop-six"
created: "2026-11-05T17:56:59.741058-05:00"
status: "published"
fingerprint: "92c402ede1ca1026d834a57f5c293f096278512037f6eb85cc9e4af3d99ed47d"
---

Actual Oryx generation315 RELEASED22:55:53UTC, fresh whole-host inspection empty, no next request. Jukebox original RFC smoke PASSED: actual UART0/VBlank/I2C vectors matched before invocation, erased unused0Ch expected; playback/pause/resume/normal app quit and timer restoration,429 packets=callbacks=local drains,114400 payload bytes,error0,due-high1,session=restore1,1775 compute entries,1306 TEMT-tail polls. Zero UART/backend errors. Frontend needed TERM/KILL after normal app return. This is limited functional evidence, not byte-exact PCM or performance acceptance.
Second integrity cell stopped BEFORE APP INVOCATION: MOS SAVE refuses overwrite of existing VECTORS.BIN, aborts autoexec at line3 Access denied. No keyboard app command/actions, no PCM/report; missing report message is secondary and still carries inherited JRC2 wording in collector. Explicit owned collector SIGINT entered finally, joined frontend, preserved raw; cell elapsed94.537s. C03 maxrate/C04 mismatch remain unrun, no retry/successor. Exact original ROM E07BCF57 and app8337949d unchanged; no firmware/default/hardware action. Fix future fixture by clearing stale snapshot before guest boot or unique path, not by firmware changes. Evidence /Agon/mystuff/AgonJukebox/docs/tasks/UART-004/e02-results.tar.gz and e02-evidence/, driver logs, entry-vector proof, oryx-e02-release.json. Source remains uncommitted under human gate. Earlier JSON submission was rejected as malformed before publication; this structured file is the actual substantive mail, chat summary already accepted.