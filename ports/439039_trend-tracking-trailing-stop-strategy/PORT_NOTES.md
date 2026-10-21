# #439039 Trend Tracking Trailing Stop Strategy -> `fmz_439039_pivot_supertrend_adx_rsi_long`

- FMZ source id: 439039 (lineage).
- Source: https://www.fmz.com/strategy/439039 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-17 11:19:06). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C115). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Pivot SuperTrend line, ADX, SMA and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG439039. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_factor` [2.0, 3.0] x `over_bought` [65, 55]: **4 trials**; pivot period 2, ATR 18, ADX 14, SMA 21 fixed.

## Ambiguities resolved

- Strict pivots; the source's ADX sums. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
