# #442832 Trend Following Quant Trading Strategy Based on Moving Average -> `fmz_442832_close_vs_hlc3_rsi8_extremes_1h_reversal`

- FMZ source id: 442832 (lineage).
- Source: https://www.fmz.com/strategy/442832 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 13:45:49). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against its own hlc3 at RSI extremes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [8, 14] x `oversold` [30, 20]: **4 trials**; overbought 100 - oversold.

## Ambiguities resolved

- VWAP reset every bar (anchor 5): it is hlc3. Volume not used. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
