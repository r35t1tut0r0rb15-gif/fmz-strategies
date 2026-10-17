# #434562 RSI鳄鱼交易策略Alligator-RSI-Trading-Strategy -> `fmz_434562_rsi_alligator_cross`

- FMZ source id: 434562 (lineage).
- Source: https://www.fmz.com/strategy/434562 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-07 15:46:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed at entry |
| 2 | PASS | RSI crosses and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`jaw` [34, 21] x `sl_pct` [0.10, 0.05]: **4 trials**; RSI 5 / 13 and the 90 % target fixed.

## Ambiguities resolved

- Long-only bracket fixed at the fill. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
