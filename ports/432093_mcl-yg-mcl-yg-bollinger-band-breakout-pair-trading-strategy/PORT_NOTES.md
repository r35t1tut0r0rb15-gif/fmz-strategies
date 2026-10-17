# #432093 MCL-YG波动率突破交易策略MCL-YG-Bollinger-Band-Breakout-Pair-Trading-Strategy -> `fmz_432093_one_sigma_band_breakout`

- FMZ source id: 432093 (lineage).
- Source: https://www.fmz.com/strategy/432093 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-14 13:49:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C48). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger-style bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR risk-per-trade quantity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `offset` [1.0, 2.0]: **4 trials**; equal upper and lower offsets.

## Ambiguities resolved

- Close conventions as stated. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
