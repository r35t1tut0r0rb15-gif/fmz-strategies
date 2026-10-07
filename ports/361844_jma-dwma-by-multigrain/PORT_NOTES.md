# #361844 jma-dwma-by-multigrain -> `fmz_361844_jma_dwma_cross_pivot_exit`

- Source: https://www.fmz.com/strategy/361844 (PineScript v5, author ChaoZhang (multigrain indicator), FMZ last
  modified 2022-05-09 00:17:15). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; pivots confirmed one bar later. |
| 2 | PASS | MA relations only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Same author's #361794 uses the adaptive JMA (different rule). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`jma_len` [5, 7, 14] x `dwma_len` [5, 10, 20] = **9 trials**. Phase 50, power 1 fixed.

## Ambiguities resolved

- A close order on the bar its own entry is sent does nothing (no position yet); reproduced by tracking the position at the bar's start.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
