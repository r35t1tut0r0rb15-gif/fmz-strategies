# #103070 简单均线策略Moving-Average-Bot-30-lines -> `fmz_103070_sma_cross_confirmed_long`

- Source: https://www.fmz.com/strategy/103070 (JavaScript, author 小草, FMZ last modified
  2020-10-13 14:51:55). Repository copy `简单均线策略Moving-Average-Bot-30-lines.md`; verbatim here
  as `original_source.md`. Read 2026-09-29.
- Status: PORTED (batch 1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | `_Cross` run length on M15 MAs; evaluated on completed bars in the port. |
| 2 | PASS | Window lengths and a bar count only. `Slippage` is execution (stored). |
| 3 | PASS | Spot; ticker bid/ask used only for order prices. |
| 4 | DONE | 99 % of balance, `Slippage`, 0.1 minimum, cancel-if-pending -> `original_sizing.txt`. |
| 5 | DECLARED | See grid. |
| 6 | REPRESENTATIVE | No duplicate group; no possible-duplicate pairs. |
| 7 | IGNORED | Description is a disclaimer only; nothing used. |

## Declared grid (criterion 5)

`fast` [3, 5, 10] x `slow` [15, 30, 60] x `enter_period` [1, 2, 3] = **27 trials**.
Every fast value is below every slow value, so no grid point is degenerate.

## Ambiguities resolved

- `FREQ = "15min"` because the code fetches `PERIOD_M15` records; the backtest header's `1d`
  period is FMZ's chart setting and does not feed the signal.
- `_Cross` semantics (run length, equality breaks the run) are taken from FMZ's API behaviour
  as used here; the port's `_signed_run` implements exactly that.
- Description notes it "included template (function with $.)"; the code shown calls only
  built-ins, so nothing else is needed.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`. Fast/slow moving-average cross with a confirmation count: moving-average trend following. Same family as #42451.
Added 2026-10-03 in the contract fix pass.
