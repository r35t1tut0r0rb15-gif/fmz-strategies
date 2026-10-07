# #362327 Hull-4ema -> `fmz_362327_hma_local_extreme_cross`

- Source: https://www.fmz.com/strategy/362327 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-10 23:47:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; local extremes known one bar later. |
| 2 | PASS | HMA relations only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [14, 21, 34, 55] = **4 trials**.

## Ambiguities resolved

- The 4 EMAs, Bollinger bands and divergence labels are display only.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
