# #362654 RSI & BB'de aynı anda Oversold Yakalama -> `fmz_362654_rsi_bb_extreme_inverse`

- Source: https://www.fmz.com/strategy/362654 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-12 17:48:21). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A8). Not run.

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

`rsi_period` [7, 14] x `bb_period` [20, 40] x `bb_mult` [1.5, 2.0] = **8 trials**. RSI levels 32 / 70 stay at the originals.

## Ambiguities resolved

- The bearish condition enters long and the bullish one short: inverted relative to the names, kept as written.
- Population stdev; Wilder RSI.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks (2026-10-07)

`none`
