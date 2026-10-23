# #442224 Multi factor Intelligent Trading Strategy -> `fmz_442224_rsi_and_sma20_joint_cross_long_only`

- FMZ source id: 442224 (lineage).
- Source: https://www.fmz.com/strategy/442224 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-20 14:03:36). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Simultaneous RSI and SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`oversold` [30, 40] x `overbought` [70, 60]: **4 trials**; RSI 14, SMA 20.

## Ambiguities resolved

- Only RSI and the SMA feed orders. Volume not used. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
