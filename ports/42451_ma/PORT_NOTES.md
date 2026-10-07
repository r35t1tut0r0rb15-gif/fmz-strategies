# #42451 Ma单均线趋势交易 -> `fmz_42451_sma_slope_long`

- Source: https://www.fmz.com/strategy/42451 (JavaScript, author ipqhjjybj, FMZ last modified
  2017-06-04 21:55:07). Repository copy `Ma单均线趋势交易.md`; verbatim here as
  `original_source.md`. Read 2026-09-29.
- Status: PORTED (batch 1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS (with note) | Polls the forming bar; the rule (SMA ratio vs 1 +/- 1e-6) is evaluated on completed bars in the port. |
| 2 | PASS | One window length and a dimensionless ratio band. |
| 3 | PASS | Spot; ticker used only for order prices. |
| 4 | DONE | All-in buy, sell all, `minMoney`, `SlidePrice`, rounding -> `original_sizing.txt`. |
| 5 | DECLARED | One parameter; see grid. |
| 6 | REPRESENTATIVE | No duplicate group; no possible-duplicate pairs. |
| 7 | IGNORED | No performance claim in the source. |

## Declared grid (criterion 5)

`ma_length` [30, 60, 120, 240] = **4 trials**. A doubling ladder through the original 120.

## Ambiguities resolved

- Header comment promises shorts when the MA falls; the code is long-only. The port follows the
  code. A short variant is not declared (it would be a different strategy).
- `trailingPrcnt` is unused in the original code and is not ported.
- `FREQ = "bar_size_pending"` (was `"1h"` until 2026-10-07): the source declares no period. Rule 2026-10-07: never choose a bar size; mark `bar_size_pending`. Logic unchanged.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`. Long while a moving average points up, out when it points down: moving-average trend following. Same family as #103070 (dual-MA cross), which is the same logic with a second average.
Added 2026-10-03 in the contract fix pass.

## Marks (2026-10-07)

`bar_size_pending`
