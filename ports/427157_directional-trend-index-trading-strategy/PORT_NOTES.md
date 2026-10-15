# #427157 Directional Trend Index Trading Strategy -> `fmz_427157_directional_trend_index`

- FMZ source id: 427157 (lineage).
- Source: https://www.fmz.com/strategy/427157 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 17:07:55). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Ratio of smoothed moves (dimensionless). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`r` [14, 25] x `level` [45, 30] x `s` [10, 5]: **8 trials**; defaults 14 / 45 / 10 (the source's); u 5 fixed; the levels are symmetric (+-level).

## Ambiguities resolved

- Contrarian as written: DTI above +45 sells, below -45 buys.
- First-bar differences count as 0; DTI 0 where its denominator is 0.
- Always in the market (REVERSAL INTENDED). FREQ = "4h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
