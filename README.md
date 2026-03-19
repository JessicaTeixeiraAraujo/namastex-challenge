# Challenge: Triage Agent (Genie + Omni)

This repository contains the final technical challenge delivery in `namastex-challenge/`.

The project was built using the `genie/` and `omni/` repositories as methodological and technical references:

- `omni/` guided the input/output contract, event flow, and WhatsApp integration
- `genie/` guided the wish model, team-lead setup, AGENTS instructions, and autonomous agent operation

The final delivery itself is isolated and organized in this repository.

## Delivery Summary

This delivery is ready for technical evaluation of the bridge/router, triage logic, and controlled fallback orchestration.

What was validated in this environment:

- project HTTP server running
- `healthcheck` at `/healthz`
- triage routing for `OPEN_TICKET`, `REQUEST_INFORMATION`, and `HIGH_SCALABLE`
- attempted execution through Genie
- controlled OpenAI fallback when the official Genie provider is unavailable
- evidence script executing the three main scenarios

The official flow `WhatsApp -> Omni -> Genie -> Omni -> WhatsApp` remains the target architecture. In the current environment, the most stable and reproducible demonstration is the local bridge with OpenAI fallback enabled.

The delivered agent satisfies the requested flow by:

- receiving messages coming from WhatsApp through Omni
- normalizing the payload into a canonical contract
- forwarding the decision to Genie when orchestrated mode is enabled
- returning the final response through Omni
- recording logs correlated by `conversation_id`

## Executive Summary for the Review Board

This delivery implements the triage agent `bridge/router`, with a canonical input/output contract, integration prepared for `Genie` as the orchestrator, and structured delivery to the `Omni` channel. In the current environment, we validated the local end-to-end operation of the agent, including `healthcheck`, logs correlated by `conversation_id`, triage classification across three scenarios, and controlled OpenAI fallback when the official Genie provider is unavailable. The target architecture remains `WhatsApp -> Omni -> Genie -> Omni -> WhatsApp`, and the repository is prepared for that operation as soon as the external infrastructure is available.

## Technical Limitations Encountered

- `Omni` could not be fully validated end-to-end in this Windows environment because of a path resolution issue in the server migrations, which prevented the API from starting correctly.
- The alternative of running `Omni` through `WSL` was blocked by difficulty installing the `Ubuntu` distribution in the local environment.
- The official `Genie` provider depends on `Claude`, and runtime execution was unavailable because of an external billing/credit restriction on the account.
- Because of those external factors, the final validation of `WhatsApp -> Omni -> Genie -> Omni -> WhatsApp` could not be completed in this specific environment, although the bridge, triage logic, and controlled fallback are operational and evidenced locally.

## Next Steps

1. Start `Omni` in a stable Linux/WSL environment.
2. Generate `OMNI_API_KEY`.
3. Connect and obtain `OMNI_INSTANCE_ID`.
4. Validate the real WhatsApp flow.
5. Capture screenshots and a short video of the complete operation.

## Delivery Status Matrix

| Criterion | Status | Notes |
|---|---|---|
| Agent implemented with Genie | Partial | Genie integration is prepared and the team was created, but the official provider (`Claude`) was not available in runtime because of billing restrictions. |
| Receives messages via Omni | Partial | The contract and webhook are prepared, but Omni was not validated end-to-end in this environment. |
| Processes the defined task | Met | Triage worked across the `OPEN_TICKET`, `REQUEST_INFORMATION`, and `HIGH_SCALABLE` scenarios. |
| Responds back through Omni | Partial | Structured reply delivery was implemented, but the full Omni/WhatsApp validation did not complete in this environment. |
| Continuous operation with monitoring | Partial | Healthcheck, logs, and runbook were delivered, but full continuous operation still depends on Omni infrastructure. |
| End-to-end flow `WhatsApp -> Omni -> Genie -> Omni -> WhatsApp` | Not Met | This was not validated live because of Omni startup issues on Windows and unavailability of the official Genie provider. |
| Genie team/agent created with clear instructions | Met | `AGENTS.md` and the Genie wish were delivered and the team was created. |
| Fallback criteria defined | Met | Friendly fallback behavior was implemented, and OpenAI fallback was validated. |
| Logs with `conversation_id` | Met | Local logs and evidence were generated with correlation. |
| Evidence of operation | Met | `run_evidence.py`, `healthz`, and logs were saved as local evidence. |
| Operational runbook delivered | Met | `README.md`, `RUNBOOK.md`, and `CHECKLIST.md` were delivered. |

## Structure

- `src/app.py`: HTTP server (bridge/router)
- `src/genie_client.py`: Genie integration through CLI
- `src/triage.py`: triage logic (screening + decision)
- `src/rag.py`: simple RAG based on a local knowledge base
- `data/policies.json`: minimal policy dataset for responses
- `RUNBOOK.md`: operations (start/stop/restart/health)
- `CHECKLIST.md`: DoD and smoke test
- `.genie/wishes/triagem-omni/wish.md`: Genie wish
- `AGENTS.md`: agent instructions (Genie)

## Reference Architecture

```text
WhatsApp -> Omni -> Bridge/Router (this repo) -> Genie
                                       <- Omni (send message) <- Bridge/Router
```

## Challenge Alignment

- `Omni`: inbound and outbound message channel
- `Bridge/Router`: implemented in this repository for validation, correlation, and routing
- `Genie`: autonomous agent orchestrator when `GENIE_ENABLED=true`

## How The Review Board Should Read This Delivery

- `namastex-challenge/` is the final artifact to execute and evaluate
- `genie/` and `omni/` were used as the design, contract, and operational reference base
- the wish and `AGENTS.md` were kept here to make the orchestration strategy explicit

## Quick Start

1. Create a `.env` file based on `.env.example`.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the server:

```bash
python -m uvicorn src.app:app --host 0.0.0.0 --port 8080
```

4. Configure an Omni webhook pointing to:

```text
POST http://<host>:8080/omni/webhook
```

CLI example:

```bash
omni automations create --name "triage-webhook" --trigger "message.received"   --action webhook --action-config '{"url":"http://<host>:8080/omni/webhook"}'
```

## Genie As Orchestrator

1. Enable in `.env`:

```text
GENIE_ENABLED=true
GENIE_TEAM=omni-whatsapp
GENIE_AGENT=team-lead
```

2. Start a Genie team lead in the `namastex-challenge` repo:

```bash
genie
/wish build an autonomous agent integrated with omni for whatsapp support
genie team create omni-whatsapp --repo . --wish triagem-omni
```

3. Ensure the team lead always responds in this format:

```text
GENIE_JSON: {"conversation_id":"...","reply":"...","handoff":false,"tags":["whatsapp","triage"]}
```

## Local Validation

```bash
python scripts/run_tests.py
```

## Quick Evidence

With the server running, execute the three main demonstration scenarios:

```bash
python scripts/run_evidence.py
```

The script automatically validates the `OPEN_TICKET`, `REQUEST_INFORMATION`, and `HIGH_SCALABLE` cases against the local `POST /omni/webhook` endpoint.

## What The Evidence Proves

The evidence generated in `evidence/` demonstrates that:

- the agent HTTP server is active and responds to `healthcheck`
- the `POST /omni/webhook` endpoint receives and processes messages using the canonical contract
- triage correctly classifies the three main scenarios (`OPEN_TICKET`, `REQUEST_INFORMATION`, and `HIGH_SCALABLE`)
- the response flow returns `conversation_id`, `reply`, `handoff`, and `tags`
- OpenAI fallback is triggered when execution through the official Genie provider is unavailable
- execution remains auditable through `logs/triage.log`

Recommended files to present to the review board:

- `evidence/healthz.json`
- `evidence/run_evidence.txt`
- `evidence/triage.log`

## OpenAI Test Mode

Without changing the officially documented Genie + Claude flow, this repository also supports an optional OpenAI fallback to unblock bridge testing.

1. Fill in the following values in `.env`:

```env
OPENAI_FALLBACK_ENABLED=true
OPENAI_API_KEY=<your-key>
OPENAI_MODEL=gpt-4o-mini
```

2. Keep `GENIE_ENABLED=true`.

3. If Genie fails because the official provider is unavailable, the bridge classifies the message with OpenAI and returns the response with the `openai-fallback` tag.

## Recommended Demo

For the most stable demonstration in the current environment:

1. Start the `namastex-challenge` server.
2. Set `GENIE_ENABLED=true` and `OPENAI_FALLBACK_ENABLED=true` in `.env`.
3. Run `python scripts/run_evidence.py`.
4. Show that the bridge attempts Genie and responds with `openai-fallback` when the official provider is unavailable.

## Acceptance Notes

- The `/healthz` endpoint returns status for health checks.
- The `/omni/webhook` endpoint accepts both the Omni `message.received` event and the canonical test payload.
- The `genie/` and `omni/` repositories guide the solution model, but are not imported as direct runtime dependencies inside `namastex-challenge/`.
- In this environment, the minimum recommended evidence for the review board is executing `python scripts/run_evidence.py` with all three scenarios passing.
