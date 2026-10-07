# #362667 HALFTREND + HEMA + SMA (FALSE SIGNAL) -> `fmz_362667_halftrend_hema_sma`

- Source: https://www.fmz.com/strategy/362667 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-12 17:53:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A9). Not run.

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

`sma_len` [100, 150, 200] x `hema_len` [40, 50, 60] = **9 trials**. HalfTrend amplitude 1 and ATR 100 stay at the originals.

## Ambiguities resolved

- HalfTrend highPrice/lowPrice = rolling high/low of `amplitude` bars; the signal needs ATR(100) (arrow not na).
- "Full candle outside the HEMA" (default false) -> body test; SMA plot offset is display only.
- `FREQ = "5min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
