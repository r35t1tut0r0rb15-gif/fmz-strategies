# #446753 VWAP均线交叉动态ATR止损止盈策略-VWAP-Moving-Average-Crossover-with-Dynamic-ATR-Stop-Loss-and-Take-Profit-Strategy -> `fmz_446753_rolling_vwap40_cross_atr_bracket_reversal`

- FMZ source id: 446753 (lineage).
- Source: https://www.fmz.com/strategy/446753 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-01 10:51:46). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V29). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Rolling-VWAP crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`vwap_period` [40, 20] x `tp_mult` [3.0, 2.0]: **4 trials**; ATR 14, SL 1.5.

## Ambiguities resolved

- Bracket fixed at the signal close. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`coarse_bar_stop`
