# #474976 均值回归增强型MACD-ATR策略Enhanced-Mean-Reversion-Strategy-with-MACD-ATR-Implementation -> `fmz_474976_bb20_reentry_macd_filter_atr_bracket_reversal`

- FMZ source id: 474976 (lineage).
- Source: https://www.fmz.com/strategy/474976 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-13 11:41:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C227). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the ATR bracket from the fill |
| 2 | PASS | Band re-entries with a MACD filter and an ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 50] x `atr_mult` [1.5, 2.5]: **4 trials**; MACD fixed.

## Ambiguities resolved

- ATR of the bar before the fill; the per-bar ATR moves pending. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
