# Checklist - Definition of Done (DoD)

- [ ] End-to-end flow validated: WhatsApp -> Omni -> Genie -> Omni -> WhatsApp.
- [x] Genie team/agent created with clear behavioral instructions.
- [x] Fallback criteria defined with a friendly user-facing message.
- [x] Logs enabled for auditability and `conversation_id` correlation.
- [x] Local evidence of operation available (`run_evidence.py` + logs).
- [x] Operational runbook delivered (start/stop/restart/health).

## How The Review Board Should Read This

- `namastex-challenge/` is the final executable delivery.
- `omni/` and `genie/` were used as methodological references for the flow, contracts, and operations.
- The central acceptance criterion is observing autonomous processing without manual intervention in the response content.

## Current Status For The Review Board

- The main repository delivery is operational locally.
- The Genie orchestration path is designed and integrated into the bridge.
- The OpenAI fallback is validated and serves as the stable demonstration path in the current environment.
- The official Omni flow still depends on external infrastructure availability and the official Genie provider during presentation time.

## Evidence Placeholders

- [ ] Screenshot of Omni receiving the event
- [ ] Screenshot of Genie processing the message
- [ ] Screenshot of WhatsApp receiving the reply
- [ ] Log with `conversation_id`
- [ ] Short video (optional)

## Validated Locally

- [x] Bridge `healthcheck` at `/healthz`.
- [x] `OPEN_TICKET` processing with `open_ticket` tag.
- [x] `REQUEST_INFORMATION` processing with `request_information` tag.
- [x] `HIGH_SCALABLE` processing with response based on `data/policies.json`.
- [x] `python scripts/run_evidence.py` executing the three scenarios successfully.
