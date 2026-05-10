# OS-PM API Key Setup Guide

**Audience:** OS-PM users
**Last updated:** 2026-05-10
**Status:** OS-PM v0.1.0 supports **two VLM backends** — OpenRouter (recommended) and Anthropic direct. Either key unlocks Phase 2 VLM mode.

> **TL;DR.** If you already have an `OPENROUTER_API_KEY` (e.g., from Perplexity / LiteLLM workflows), you can activate VLM mode in 30 seconds. No new account, no separate billing. See §1 below.

---

## 0. Decision tree

```
Do you have OPENROUTER_API_KEY already?
  ├── YES  → §1 (recommended)  ← ★ start here
  └── NO   → Do you want pay-per-call directly with Anthropic?
              ├── YES → §2
              └── NO  → §3 (apply for Claude for Science academic credit)
```

OS-PM is designed so any of these unlocks VLM mode without code changes; you only edit `.env`.

---

## 1. OpenRouter — recommended path

### 1.1 Get a key (skip if you already have one)

1. Visit https://openrouter.ai/keys
2. Sign up (Google / GitHub / email OK)
3. Add a credit card OR redeem free credits
4. **Create Key** → copy `sk-or-v1-...`

### 1.2 Register the key locally

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
Copy-Item .env.example .env -ErrorAction SilentlyContinue
# Edit .env and set:
#   OPENROUTER_API_KEY=sk-or-v1-...
#   VLM_BACKEND=openrouter        (or leave VLM_BACKEND=auto)
```

### 1.3 Verify

```powershell
cd "C:\Users\geniu\Documents\Obsidian Vault\Using Antigravity\ospm"
python -c "
from backend.app.config import get_settings
from backend.app.modules.vlm_client import VLMClient
s = get_settings()
print('OpenRouter key set :', bool(s.openrouter_api_key))
print('Backend            :', s.vlm_backend)
c = VLMClient()
print('Selected backend   :', c._kind)
print('Model id           :', c._resolve_model_id())
"
```

Expected output:

```
OpenRouter key set : True
Backend            : auto
Selected backend   : openrouter
Model id           : anthropic/claude-sonnet-4.6
```

### 1.4 Run the Natanz retrofit in VLM mode

```powershell
python -m scripts.natanz_retrofit --vlm
```

Expected behaviour:
- Heuristic mode posterior was 0.492 with two false-positive geophysical-centrifuge papers.
- VLM mode should **read each abstract** and (for the most prominent geocentrifuge papers) classify them as unrelated → fewer/no indicators → posterior either correctly low or backed by genuinely relevant papers.

### 1.5 Cost

| Model | OpenRouter $ / 1M input tok | $ / 1M output tok |
|-------|-----------------------------|---------------------|
| `anthropic/claude-sonnet-4.6` | ~$3.15 | ~$15.75 |
| `anthropic/claude-haiku-4.5`  | ~$1.05 | ~$5.25  |
| `anthropic/claude-opus-4.7`   | ~$15.75 | ~$78.75 |

Phase 1 single retrofit run on 50 OpenAlex hits: **~$0.20–0.50**. Set a daily limit at https://openrouter.ai/settings/credits.

### 1.6 Caveats

- **Prompt caching** is partially supported — OpenRouter passes Anthropic `cache_control` headers but the discount isn't always realised. For Phase 1 (small volumes) this is negligible; for Phase 2 imagery batches consider switching to Anthropic direct (§2).
- **Rate limits** are per-account, generally more permissive than a freshly-created Anthropic Console account.
- **Region** — OpenRouter routes via the original provider. Sanctioned-region users may be blocked at the edge.

---

## 2. Anthropic direct — when prompt caching matters

### 2.1 Eligibility

- Same email/SSO as your Claude.ai Max plan login is fine — the Console
  is at console.anthropic.com but uses unified Anthropic identity.
- **Max plan does NOT include API credit.** Console billing is separate.

### 2.2 Get a key

1. https://console.anthropic.com/keys → Create Key
2. Add a payment method (separate from Max plan)
3. Set a per-day spend limit (e.g., $5) before you walk away

### 2.3 Register locally

```powershell
# In ospm/.env
ANTHROPIC_API_KEY=sk-ant-api03-...
VLM_BACKEND=anthropic           # force this backend even if OpenRouter is set
```

### 2.4 Verify (same script as §1.3, expect `Selected backend: anthropic`).

### 2.5 Cost — full prompt-caching applies

Phase 1 single retrofit run: **~$0.05–0.20** (caching the system prompt across 50 calls).

---

## 3. Claude for Science — academic credit

For projects targeting peer-review publication. Approval typically takes 1–4 weeks.

1. Application form: search "Anthropic Claude for Science" — application page lives on anthropic.com/research.
2. Apply with the OS-PM project description (see `Claude_for_Science_application.md`).
3. On approval, credits show up in your Console account; switch to §2 (Anthropic direct) once active.

This route is recommended **after** Phase 2 imagery activation when monthly burn is justifiable.

---

## 4. Switching between backends mid-project

`VLM_BACKEND=auto` (default) prefers OpenRouter when both keys are set. Override per-call:

```python
from backend.app.modules.vlm_client import VLMClient

c_oa = VLMClient(backend="openrouter")
c_an = VLMClient(backend="anthropic")  # requires ANTHROPIC_API_KEY in .env
```

Useful for the Phase 2 ablation (`scripts/phase2_ablation.py`) when you want to compare both backends head-to-head on the same case.

---

## 5. Security checklist

- [ ] `.env` is in `.gitignore` (it is — verify with `git check-ignore .env`)
- [ ] Daily spend limit set on each account
- [ ] Key rotation every 90 days
- [ ] Obsidian / cloud sync excludes `.env` (verify if Vault is synced)
- [ ] Console / OpenRouter usage dashboard reviewed weekly during Phase 2
- [ ] Old keys revoked when rotated

---

## 6. Troubleshooting

### 401 Unauthorized

```
openai.AuthenticationError: ... or anthropic.AuthenticationError: ...
```

- Re-copy key (no trailing whitespace, no surrounding quotes in `.env`)
- For OpenRouter: keys start `sk-or-v1-`
- For Anthropic: keys start `sk-ant-api03-` (or older `sk-ant-`)

### Rate limit (429)

- OpenRouter: add credits or wait
- Anthropic: new accounts start at 5 RPM/40k TPM. The retry decorator (`tenacity`) handles transient cases; persistent failure → request a tier upgrade in Console.

### Model not found

- For OpenRouter, browse https://openrouter.ai/models to pick the exact `provider/model` id
- Override in `.env`: `PRIMARY_VLM=anthropic/claude-haiku-4.5` (with the `/`) — `_resolve_model_id` honours pre-prefixed ids verbatim

### Prompt caching does nothing on OpenRouter

- Use the Anthropic-direct backend (§2) when you need 90% caching discounts at scale
- `VLM_BACKEND=anthropic` + ensure `ANTHROPIC_API_KEY` is set

---

## 7. Memory hand-off

This guide pairs with the persistent memory entry
`~/.claude/projects/.../memory/ospm_api_key_procedure.md` so future sessions can pick up activation steps automatically. If you change backends, re-read that memo or update it with the new state.
