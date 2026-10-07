# #361521 Indicator-WaveTrend-Oscillator -> `fmz_361521_wavetrend_extremes_reverse`

- Source: https://www.fmz.com/strategy/361521 (PineScript, LazyBear's WaveTrend with orders added;
  FMZ last modified 2022-05-08 11:16:55). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Pine bar-close evaluation, next-open fills. |
| 2 | PASS (screen: REVIEW) | The "level" inputs are oscillator levels, not prices. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n1` [7, 10, 14] x `ob_level` [40, 53, 60] = **9 trials** (40 is the backtest header's value).
`n2` 21 fixed.

## Ambiguities resolved

- No warm-up guard in the source; the port emits nothing for the first n1+n2 bars.
- `FREQ = "1h"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks (2026-10-07)

`none`
