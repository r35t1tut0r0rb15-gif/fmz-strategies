# #361783 Engulfing-Candles -> `fmz_361783_engulfing_reverse`

- Source: https://www.fmz.com/strategy/361783 (PineScript v3, author ChaoZhang, FMZ last
  modified 2022-05-08 10:57:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Candle pattern on completed bars. |
| 2 | PASS | Price comparisons within the bars. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | The commented block's fixed qty is inactive. |
| 5 | DECLARED | No inputs; declared variants. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`min_body_atr` [0, 0.25, 0.5] = **3 trials**; 0 is the source exactly, the others are declared starting variants (minimum engulfing body in ATR(14)).

## Ambiguities resolved

- The commented `strategy.exit(profit=1000, loss=50)` lines are not active and are not ported.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
