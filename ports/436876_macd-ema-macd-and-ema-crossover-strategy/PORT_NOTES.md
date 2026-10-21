# #436876 MACD和EMA金叉死叉策略MACD-and-EMA-Crossover-Strategy -> `fmz_436876_macd_zero_side_ema_bracket`

- FMZ source id: 436876 (lineage).
- Source: https://www.fmz.com/strategy/436876 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-28 15:22:14). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | EMA-distance bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `ema_len` [200, 100]: **4 trials**; slow 26, signal 9 and the 2x target fixed.

## Ambiguities resolved

- EMA bracket as distances from the signal close; shorts only from flat as written. REVERSAL INTENDED (longs). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
