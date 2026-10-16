# #428802 基于VSTOP和RSI的交易策略VSTOP-and-RSI-Trading-Strategy -> `fmz_428802_rsi2_momentum_vstop`

- FMZ source id: 428802 (lineage).
- Source: https://www.fmz.com/strategy/428802 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 15:48:46). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [2, 3] x `mult` [2.0, 3.0]: **4 trials**; 30 / 70 and Vstop ATR length 2 fixed.

## Ambiguities resolved

- nz() seeds as written; na ATR makes the line na (no short filter) until it exists.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
