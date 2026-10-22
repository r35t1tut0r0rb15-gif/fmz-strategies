# #458128 Three Week High Low Momentum Trading Strategy -> `fmz_458128_high30_vs_close30_buy_close1_sell_long`

- FMZ source id: 458128 (lineage).
- Source: https://www.fmz.com/strategy/458128 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 10:44:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | 30-bar high and close comparisons |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [30, 15]: **2 trials**.

## Ambiguities resolved

- Call order followed (entry, then close). Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
