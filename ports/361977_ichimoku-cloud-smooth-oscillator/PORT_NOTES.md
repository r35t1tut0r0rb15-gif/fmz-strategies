# #361977 Ichimoku-Cloud-Smooth-Oscillator -> `fmz_361977_t3_cloud_oscillator_side`

- Source: https://www.fmz.com/strategy/361977 (PineScript, author ChaoZhang, FMZ last
  modified 2022-05-09 12:22:38). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; displaced values are past values. |
| 2 | PASS | Relative distances to the cloud only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. Different from #55839 (classic Ichimoku with Donchian lines). |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [7, 9, 12] x `base` [20, 26, 34] = **9 trials**. Span 52, displacement 26, T3 b 0.7 fixed.

## Ambiguities resolved

- Asymmetric distance for negative values (dist - h/2) kept; only the sign is used by the orders, so it only shifts the dead zone.
- Warm-up: no orders before span2 + displacement bars.
- `FREQ = "2h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks (2026-10-07)

`none`
