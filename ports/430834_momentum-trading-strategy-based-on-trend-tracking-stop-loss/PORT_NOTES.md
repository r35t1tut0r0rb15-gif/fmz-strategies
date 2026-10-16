# #430834 Momentum Trading Strategy Based on Trend Tracking Stop Loss -> `fmz_430834_supertrend_rsi_momentum_long`

- FMZ source id: 430834 (lineage).
- Source: https://www.fmz.com/strategy/430834 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 13:59:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C39). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR band and an RSI level. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [5.0, 3.0] x `rsi_level` [60, 55]: **4 trials**; ATR period 1 and RSI 14 fixed.

## Ambiguities resolved

- Header period used. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
