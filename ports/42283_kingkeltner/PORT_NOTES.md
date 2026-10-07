# #42283 KingKeltner趋势策略_低频 -> `fmz_42283_kingkeltner_breakout`

- Source: https://www.fmz.com/strategy/42283 (JavaScript, author ipqhjjybj; the code header says
  it is ported from vnpy). FMZ last modified 2017-06-02 23:06:08. Repository copy
  `KingKeltner趋势策略_低频.md`; verbatim here as `original_source.md`. Read 2026-09-29.
- Status: PORTED (batch 1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | The bot polls the forming bar. The rule (`Close > SMA + k*ATR`; close-based trailing exit) is written on bar fields, so the port evaluates it on each completed bar and the engine fills at the next open. |
| 2 | ADAPT | The 15 % trailing distance becomes `trail_atr` x ATR(KK_Length). Channel is already ATR-scaled. |
| 3 | PASS | Spot; ticker used only for order prices. |
| 4 | DONE | All-in buy, `minMoney` guard, `SlidePrice`, quantity rounding -> `original_sizing.txt`. The trailing exit is the strategy's only exit and is evaluated on closes, so it is ported as a signal (README rule) and also quoted in the sizing file. |
| 5 | DECLARED | See grid below. |
| 6 | REPRESENTATIVE | No duplicate group; no possible-duplicate pairs. |
| 7 | IGNORED | No performance claim in the source. |

## Declared grid (criterion 5)

`kk_length` [10, 20, 40] x `kk_dev` [1.0, 1.5, 2.0] x `trail_atr` [3, 6, 12] = **27 trials**.

- `kk_length`: original 11; a doubling ladder covers short to medium windows.
- `kk_dev`: original 1.3, bracketed.
- `trail_atr`: the original 15 % has no fixed ATR equivalent (it depends on the instrument's
  volatility and bar size). A doubling ladder of 3/6/12 ATR is declared instead. DEFAULT uses 6.

## Ambiguities resolved

- Running high starts at the signal bar's high (original line 111), then includes every bar
  in the position.
- Position state is tracked inside `simulate` exactly as the engine will fill it (entry at the
  next open, exit at the next open), so exit signals are only emitted while the engine is long.
- `FREQ = "bar_size_pending"` (was `"1h"` until 2026-10-07): the source declares no period ("低频" = low frequency). Rule 2026-10-07: never choose a bar size; mark `bar_size_pending`. Logic unchanged.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`. Close breaking an ATR-scaled band around a moving average (Keltner-type channel breakout).
Added 2026-10-03 in the contract fix pass.

## Marks (2026-10-07)

`bar_size_pending`
