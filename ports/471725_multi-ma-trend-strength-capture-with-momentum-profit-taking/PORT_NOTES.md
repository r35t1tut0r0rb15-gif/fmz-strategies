# #471725 Multi MA Trend Strength Capture with Momentum Profit Taking Strategy -> `fmz_471725_sma5_25_cross_sma75_adx_sudden_move_exit_reversal`

- FMZ source id: 471725 (lineage).
- Source: https://www.fmz.com/strategy/471725 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 17:18:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C211). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with trend and ADX filters, sudden-move exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`move_pct` [0.006, 0.01] x `adx_th` [20, 25]: **4 trials**; the SMA lengths fixed.

## Ambiguities resolved

- The script's own DM terms; call order followed. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
