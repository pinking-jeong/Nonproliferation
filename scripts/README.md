# Scripts

## natanz_retrofit.py

Retrospective test — does pre-2002 open-source data alone raise an enrichment hypothesis at Natanz coordinates?

```bash
# Offline / heuristic (no API key needed)
python -m scripts.natanz_retrofit --no-vlm

# With Claude VLM classification
export ANTHROPIC_API_KEY=sk-ant-...
python -m scripts.natanz_retrofit --vlm
```

Output written to `./data/natanz/natanz_retrofit_report.json`.

### Validation criterion (MVP)

The system PASSES if: pre-2002 evidence alone yields a `gas_centrifuge` hypothesis with posterior ≥ 0.4.

### Notes

- Landsat-7 (pre-2002 era) STAC archive: `landsat-c2-l2` on Planetary Computer
- OpenAlex `institutions.country_code:IR` for Iran-affiliated authors
- VLM mode adds ~10s and ~$0.05 per paper classified (Claude 4.6 Sonnet)
