# Runbook - Triage Agent

This runbook describes the operation of the final delivery in `namastex-challenge/`.

## Start

```bash
python -m uvicorn src.app:app --host 0.0.0.0 --port 8080
```

If you are using Genie as the orchestrator:
1. Adjust `.env` with `GENIE_ENABLED=true`.
2. Start the team lead with:
```bash
genie team create omni-whatsapp --repo . --wish triagem-omni
```

## Delivery Context

This challenge was built using these repositories as reference:

- `C:/GitHub/namastex/genie`
- `C:/GitHub/namastex/omni`
- `C:/GitHub/namastex/namastex-challenge`

Intended usage of each one:

- `omni/`: reference for event contracts, automations, API, and WhatsApp channel operations
- `genie/`: reference for wish, team lead, autonomous team, and agent operation
- `namastex-challenge/`: final implementation delivered to the review board

## Demonstration Scope

This runbook covers two presentation modes:

1. target flow: `WhatsApp -> Omni -> Genie -> Omni -> WhatsApp`
2. demonstrable flow in the current environment: `Bridge -> Genie attempt -> OpenAI fallback`

For the review board, the second mode should be treated as the main demonstration whenever the official Genie provider or the full Omni infrastructure is unavailable during the presentation.

## Operational Prerequisites

In `.env`, validate at least:

```env
OMNI_BASE_URL=http://localhost:8882
OMNI_API_KEY=...
OMNI_INSTANCE_ID=...
GENIE_ENABLED=true
GENIE_TEAM=omni-whatsapp
GENIE_AGENT=team-lead
OPENAI_FALLBACK_ENABLED=true
OPENAI_API_KEY=...
```

## Healthcheck

```bash
curl http://localhost:8080/healthz
```

Expected response:

```json
{"status":"ok","genie_enabled":true,"openai_fallback_enabled":true,"omni_base_url":"http://localhost:8882"}
```

## Stop

Interrupt the process with `Ctrl+C` in the terminal where it is running.

## Restart

1. Stop the process.
2. Run the Start command again.

## OpenAI Fallback Demo Mode

If the official Genie provider is unavailable, use the controlled fallback below for the demonstration:

1. Keep `GENIE_ENABLED=true`.
2. Enable `OPENAI_FALLBACK_ENABLED=true`.
3. Fill `OPENAI_API_KEY` in `.env`.
4. Run `python scripts/run_evidence.py` to validate the `OPEN_TICKET`, `REQUEST_INFORMATION`, and `HIGH_SCALABLE` scenarios.

## Review Board Smoke Test

Target flow:

1. Send a WhatsApp message to the number connected in Omni.
2. Confirm the `message.received` event in Omni.
3. Confirm receipt at the `/omni/webhook` endpoint.
4. Confirm processing through Genie using `genie read`, `genie inbox`, or team lead logs.
5. Confirm delivery through Omni `/api/v2/messages`.
6. Confirm the reply arriving back in WhatsApp.

Demonstrable flow in this environment:

1. Start the `namastex-challenge` server.
2. Enable `GENIE_ENABLED=true` and `OPENAI_FALLBACK_ENABLED=true`.
3. Run `python scripts/run_evidence.py`.
4. Show the three approved scenarios and the returned response tags.

## Recommended Evidence

- Screenshot of WhatsApp receiving the reply
- Screenshot of Omni registering inbound and outbound events
- Bridge log with `conversation_id`
- Genie team lead log or inbox output
