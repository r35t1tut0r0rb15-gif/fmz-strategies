# #364518 Buy&Sell Strategy depends on AO+Stoch+RSI+ATR -> `fmz_364518_ao_stoch_rsi_atr_bracket`

- Source: https://www.fmz.com/strategy/364518 (PineScript v4, author ChaoZhang, FMZ last
  modified 2022-05-20 16:19:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG364518` (Jaccard >= 0.80) with #380330 (DUPLICATE), #380337 (DUPLICATE), #429567 (DUPLICATE); best Jaccard 0.922 with #380337. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_k` [9, 14] x `rsi_len` [7, 10, 14] x `atr_len` [14, 28] = **12 trials**. AO 3/17 and stoch smoothing 3 stay at the originals.

## Ambiguities resolved

- Stop = signal-bar low - ATR, target = close + ATR (shorts mirrored) -> `sl_stop`/`tp_stop` fractions, shifted one bar in stops().
- A repeated same-side signal re-sets the levels in Pine; vbt keeps the entry levels: mark `trailing_stop_pending`.
- AO scale factor x1000 does not change its sign tests.
- `FREQ = "30min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks (2026-10-07)

`trailing_stop_pending`
