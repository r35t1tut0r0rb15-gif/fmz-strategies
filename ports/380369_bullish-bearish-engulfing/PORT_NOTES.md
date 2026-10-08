# #380369 Bullish & Bearish Engulfing -> `fmz_380369_engulfing_scaled`

- Source: https://www.fmz.com/strategy/380369 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-28 13:17:09). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Minimum body 3.0 price units -> `min_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`scale` [1.5, 2.0, 3.0] x `min_atr` [0.0, 0.25, 0.5] = **9 trials**.

## Ambiguities resolved

- Minimum body 30/10 = 3.0 price units -> `min_atr` x ATR(14) (criterion 2); about 0 ATR on BTC.
- Engulfing tests as coded (close beyond the previous open).
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`bar_size_pending`
