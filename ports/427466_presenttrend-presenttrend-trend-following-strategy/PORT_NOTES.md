# #427466 PresentTrend趋势跟随策略PresentTrend-Trend-Following-Strategy -> `fmz_427466_presenttrend_mfi14_atr1618_line_lag2_alternating_reversal`

- FMZ source id: 427466 (lineage).
- Source: https://www.fmz.com/strategy/427466 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-21 15:00:08). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MFI-switched ATR trailing line against its own lag, with alternation filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity, capital 10000, commission 0.1 %, slippage 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 20] x `multiplier` [1.618, 1.0]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
