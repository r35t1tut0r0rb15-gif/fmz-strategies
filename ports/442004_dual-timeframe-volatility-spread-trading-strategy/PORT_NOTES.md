# #442004 Dual Timeframe Volatility Spread Trading Strategy -> `fmz_442004_b_xtrender_zero_cross_own_exit_long`

- FMZ source id: 442004 (lineage).
- Source: https://www.fmz.com/strategy/442004 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 15:31:32). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Xtrender zero crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity / close quantity rule stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_sma` [7, 5] x `rsi_factor` [2, 3]: **4 trials**; the other factors fixed.

## Ambiguities resolved

- One long at a time (default pyramiding); bounded date window dropped. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
