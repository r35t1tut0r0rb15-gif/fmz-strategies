# #400134 SMA-pine语言教学策略脚本 (SMA Cross) -> `fmz_400134_sma_10_200_bracket`

- Source: https://www.fmz.com/strategy/400134 (PineScript v4, author Zer3192, FMZ last
  modified 2023-02-15 18:19:03). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | Order-size lines -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [10, 20] x `slow` [100, 200] x `pct` [0.03, 0.05] (stop = target) = **8 trials**.

## Ambiguities resolved

- 5 % stop and 5 % target on the entry price -> constant sl_stop / tp_stop fractions.
- Un-indented exit lines run every bar (same effect while in a position).
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`bar_size_pending`
