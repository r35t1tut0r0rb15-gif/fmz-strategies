# #452692 基于PSAR与EMA的量化策略-PSAR-and-EMA-Based-Quantitative-Trading-Strategy -> `fmz_452692_psar_ema30_setup_candle_level_session_bracket`

- FMZ source id: 452692 (lineage).
- Source: https://www.fmz.com/strategy/452692 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-28 11:00:40). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the fill-price bracket as fixed fractions; the flag chain in a loop |
| 2 | PASS | PSAR / EMA set-up candles with level re-crosses |
| 3 | PASS | Spot pair in the header only (the source sends shorts as written). |
| 4 | DONE | The margin settings stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [30, 50] x `sl_pct` [0.16, 0.08] x `tp_pct` [0.32, 0.16]: **8 trials**; the PSAR settings and the session fixed.

## Ambiguities resolved

- Session on the UTC bar open; bracket from the fill bar. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
