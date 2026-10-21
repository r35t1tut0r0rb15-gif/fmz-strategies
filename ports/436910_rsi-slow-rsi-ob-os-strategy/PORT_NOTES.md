# #436910 慢速RSI超买超卖策略Slow-RSI-OB-OS-Strategy -> `fmz_436910_slow_rsi_ema_levels`

- FMZ source id: 436910 (lineage).
- Source: https://www.fmz.com/strategy/436910 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-28 18:07:48). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C97). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [500, 250] x `smoother` [250, 125]: **4 trials**; levels 52 / 48 fixed.

## Ambiguities resolved

- Commented-out exits not ported. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
