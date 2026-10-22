# #442847 动量突破EMA-34交叉策略Momentum-Breakthrough-EMA-34-Crossover-Strategy -> `fmz_442847_ema34_high_low_band_cross_unit_target`

- FMZ source id: 442847 (lineage).
- Source: https://www.fmz.com/strategy/442847 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 15:05:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C162). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit target -> fraction of the signal close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 20] x `exit_frac` [0.00119, 0.01]: **4 trials**.

## Ambiguities resolved

- Price-unit target as a fraction of the latest signal close. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
