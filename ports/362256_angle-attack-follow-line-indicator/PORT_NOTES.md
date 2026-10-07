# #362256 Angle-Attack-Follow-Line-Indicator -> `fmz_362256_follow_line_flip`

- Source: https://www.fmz.com/strategy/362256 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-10 21:29:29). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the higher-timeframe line is unused in the default mode. |
| 2 | PASS | Bollinger and ATR based. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [14, 21, 34] x `bb_dev` [1, 1.5] x `atr_period` [5, 10] = **12 trials**.

## Ambiguities resolved

- Only the default mode (no higher-timeframe filter) is ported; the angle-based add/reduce signals are alerts only.
- `FREQ = "15min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks (2026-10-07)

`none`
