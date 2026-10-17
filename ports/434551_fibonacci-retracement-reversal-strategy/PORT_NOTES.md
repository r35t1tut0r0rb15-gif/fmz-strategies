# #434551 Fibonacci Retracement Reversal Strategy -> `fmz_434551_rsi_extreme_bracket`

- FMZ source id: 434551 (lineage).
- Source: https://www.fmz.com/strategy/434551 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-07 15:15:26). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C68). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | RSI levels and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `pct` [0.01, 0.02]: **4 trials**; levels 30 / 70 fixed; `pct` sets both the stop and the target.

## Ambiguities resolved

- Always-true Fibonacci tests kept as written (no effect). One percent for stop and target. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
