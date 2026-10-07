# #365668 Swing Hull/rsi/EMA Strategy -> `fmz_365668_hull_swing_ema_pullback`

- Source: https://www.fmz.com/strategy/365668 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2022-05-25 16:06:18). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Stop 750 ticks -> `sl_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | strategy() sizing / trade-size inputs -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG365668` (Jaccard >= 0.80) with #440702 (DUPLICATE); best Jaccard 0.976 with #440702. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hull_period` [250, 500] x `sl_atr` [1.0, 2.0, 3.0] = **6 trials**. RSI 14 (70/30) and EMA 59 / 96 stay at the originals.

## Ambiguities resolved

- Stop 750 ticks (instrument-specific) -> `sl_atr` x ATR(14) at the signal bar (criterion 2), an `sl_stop` fraction shifted one bar.
- RSI closes are close-based exit signals; not applied on a same-side entry bar.
- Entries gated by `not na(vrsi)`.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks (2026-10-07)

`none`
