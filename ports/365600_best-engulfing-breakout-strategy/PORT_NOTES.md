# #365600 BEST Engulfing + MA -> `fmz_365600_engulfing_ma_bracket`

- Source: https://www.fmz.com/strategy/365600 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-25 14:40:18). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | TP 2000 / SL 200 USD -> `tp_atr` / `sl_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing / trade-size inputs -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365600` (Jaccard >= 0.80) with #440459 (DUPLICATE); best Jaccard 0.950 with #440459. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [20, 32, 50] x `sl_atr` [1.0, 2.0] x `tp_atr` [5.0, 10.0] = **12 trials**.

## Ambiguities resolved

- TP 2000 / SL 200 USD (price units) -> `tp_atr` / `sl_atr` x ATR(14) at the signal bar (criterion 2), as fractions in stops() shifted one bar.
- `close[1] < MA` closes the long: close-based exit signal (rule 3), not applied on the entry bar itself.
- Date window replaced by `testPeriod() => true` in the source; pyramiding 2 never applies.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks (2026-10-07)

`none`
