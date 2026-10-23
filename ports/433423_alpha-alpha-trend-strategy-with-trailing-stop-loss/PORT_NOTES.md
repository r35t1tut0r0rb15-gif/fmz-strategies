# #433423 Alpha趋势跟踪止损策略Alpha-Trend-Strategy-with-Trailing-Stop-Loss -> `fmz_433423_alphatrend_mfi14_atr1_cross_pct_trail_reversal`

- FMZ source id: 433423 (lineage).
- Source: https://www.fmz.com/strategy/433423 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-27 15:25:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house percent trail |
| 2 | PASS | AlphaTrend line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): margin_long 100, margin_short 100, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`coeff` [1.0, 2.0] x `trail_pct` [0.10, 0.05]: **4 trials**; period 14.

## Ambiguities resolved

- Hourly-close ratchet as the house minute-close percent trail. Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "alphatrend"`.

## Marks

`trailing_stop, trailing_stop_pending`
