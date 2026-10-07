# #364001 [dev]RedK Momentum Bars -> `fmz_364001_redk_momentum_bars_zero`

- Source: https://www.fmz.com/strategy/364001 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-18 11:32:35). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 10] x `slow` [20, 30] x `filter_len` [50, 100] = **8 trials**. Delay 3 stays at the original.

## Ambiguities resolved

- All MA types default SMA; the RSS_WMA (LazyLine) option is not the default.
- Zero crossings of MA differences: scale-free.
- `FREQ = "3min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
