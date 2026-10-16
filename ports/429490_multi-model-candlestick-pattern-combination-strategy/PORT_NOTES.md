# #429490 Multi model Candlestick Pattern Combination Strategy -> `fmz_429490_noro_candle_models`

- FMZ source id: 429490 (lineage).
- Source: https://www.fmz.com/strategy/429490 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-17 15:53:06). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Candle shapes and body ratios only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_len` [10, 20] x `exit_frac` [0.5, 1.0]: **4 trials**; the three models on, doji 1/10 fixed.

## Ambiguities resolved

- Entry wins over a same-bar close_all. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
