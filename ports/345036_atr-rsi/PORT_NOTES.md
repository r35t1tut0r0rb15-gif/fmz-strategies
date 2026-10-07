# #345036 ATR-RSI组合策略 -> `fmz_345036_atr_active_rsi_swing_long`

- Source: https://www.fmz.com/strategy/345036 (JavaScript, author 一刀, FMZ last modified
  2022-02-13 17:19:57). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; the port evaluates on completed bars. |
| 2 | PASS | ATR ratio and RSI thresholds are dimensionless. |
| 3 | PASS | Spot only. |
| 4 | DONE | All-cash buy, sell all, `slide_price`, order cancelling -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`rsi_period` [12, 20, 30] x `atrma_period` [10, 18, 20] = **9 trials** (12/18 are the backtest
header's values). ATR 14 and RSI 30/70 fixed.

## Ambiguities resolved

- **Author slip kept**: the ATR average divides by `atr_period` instead of `atrma_period`, so the
  filter needs ATR above 20/14 x its 20-bar mean at the defaults. Ported as written.
- The short-history branch calls an undefined `aval` (would throw); irrelevant after warm-up.
- `FREQ = "15min"` from `GetRecords(PERIOD_M15)`.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
