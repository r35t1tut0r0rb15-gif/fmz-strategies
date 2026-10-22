# #454733 多层级RSI回归交易策略与动态波动率调整-Multi-Level-RSI-Mean-Reversion-Strategy-with-Dynamic-Volatility-Adjustment -> `fmz_454733_rsi20_big_body_pivot_break_reversion_from_flat`

- FMZ source id: 454733 (lineage).
- Source: https://www.fmz.com/strategy/454733 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-21 14:16:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C196). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the exit is a close test |
| 2 | PASS | RSI dips on big bodies under the pivot |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [20, 14] x `body_lookback` [288, 100] x `exit_frac` [0.6, 1.0]: **8 trials**; the level / ratio ladder fixed.

## Ambiguities resolved

- One trade at a time (add-ons refused); no stop. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
