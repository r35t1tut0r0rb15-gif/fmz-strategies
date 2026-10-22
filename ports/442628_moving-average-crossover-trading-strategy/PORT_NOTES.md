# #442628 Moving Average Crossover Trading Strategy -> `fmz_442628_close_ema8_cross_ema50_filter_long`

- FMZ source id: 442628 (lineage).
- Source: https://www.fmz.com/strategy/442628 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:46:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C159). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `mid` [18, 30]: **4 trials**; the EMA 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
