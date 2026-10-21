# #438785 MACD指标的RSI反转策略RSI-of-MACD-Reversal-Strategy -> `fmz_438785_rsi_of_macd_long`

- FMZ source id: 438785 (lineage).
- Source: https://www.fmz.com/strategy/438785 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-15 12:33:14). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI of MACD crossings and an EMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The risk-based quantity, stop input and percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `slow` [21, 26]: **4 trials**; MACD fast 12, signal 9 and the 30 / 35 / 15 levels fixed.

## Ambiguities resolved

- Stop input only sizes; partial exit off. Long only. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
