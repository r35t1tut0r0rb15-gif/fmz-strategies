# #446757 Volatility Trend Following Strategy -> `fmz_446757_band_atr_trend_line_flip_long`

- FMZ source id: 446757 (lineage).
- Source: https://www.fmz.com/strategy/446757 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-04-01 11:07:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band-driven ATR trend-line flips |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The 20 % of equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `dev` [1.0, 2.0]: **4 trials**; the ATR length fixed; the filter on.

## Ambiguities resolved

- Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
