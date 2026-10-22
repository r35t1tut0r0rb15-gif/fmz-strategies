# #439601 Momentum Oscillator Trend Tracking Strategy -> `fmz_439601_flash_mom_rsi_supertrend_exit`

- FMZ source id: 439601 (lineage).
- Source: https://www.fmz.com/strategy/439601 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-22 10:08:55). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C121). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the wrong-side stop read as a close signal |
| 2 | PASS | EMA stack, SuperTrend, EMA trail and RSI of momentum |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The dollar-per-position quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND437789. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mom_rsi_val` [60, 50] x `factor` [3.0, 2.0]: **4 trials**; EMA 12 trail 1 %, ATR 10 and the EMA stack fixed.

## Ambiguities resolved

- Wrong-side stop read as a close at the next open. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
