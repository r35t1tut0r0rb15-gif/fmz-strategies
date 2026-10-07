# #361996 HA-Market-Bias -> `fmz_361996_ha_bias_faded`

- Source: https://www.fmz.com/strategy/361996 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-09 14:16:37). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; same-timeframe request. |
| 2 | PASS | Average comparisons only. |
| 3 | PASS | Binance futures pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ha_len` [50, 100] x `ha_len2` [50, 100] = **4 trials**.

## Ambiguities resolved

- **Direction as written**: long when the smoothed HA open is above the smoothed HA close (the indicator's bearish colour). Flagged in the worker report.
- Warm-up: no orders before ha_len + ha_len2 bars.
- `FREQ = "10min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "heikin_ashi_trend"`.

## Marks (2026-10-07)

`none`
