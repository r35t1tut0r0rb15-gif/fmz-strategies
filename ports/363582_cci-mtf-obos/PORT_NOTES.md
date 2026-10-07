# #363582 CCI MTF Ob+Os -> `fmz_363582_cci_mtf_extreme_momentum`

- Source: https://www.fmz.com/strategy/363582 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-16 18:12:07). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [14, 20, 30] = **3 trials**. Levels +-100 and the five timeframes stay at the originals.

## Ambiguities resolved

- Lower timeframes than the 12 h chart: each CCI is the previous chart bar's last intrabar value (`[1]`); port runs on 15 m bars and decides at 12 h bar ends.
- Overbought on all timeframes enters long, oversold short: kept as written.
- `FREQ = "15min"` (lowest requested timeframe); chart 12 h from the backtest header sets decision times.

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks (2026-10-07)

`none`
