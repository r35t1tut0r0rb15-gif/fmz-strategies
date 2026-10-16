# #427390 Combined Moving Average Crossover Strategy -> `fmz_427390_t3_fibo_mavilimw`

- FMZ source id: 427390 (lineage).
- Source: https://www.fmz.com/strategy/427390 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-20 16:42:37). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry. |
| 2 | PASS | MA lengths, stop as a fraction of price. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 75 % of equity stored; the stop via `stops()`. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length1` [8, 13] x `length12` [5, 3] x `stop_loss` [3, 6]: **8 trials**; defaults 8 / 5 / 3 (the source's); volume factors 0.7 / 0.618, MavilimW 3 / 5 fixed.

## Ambiguities resolved

- Defaults switch all three tools on: only the combined branch is live.
- `barssince(...)` comparisons as written: a side opens on the first bar of a new state run after the opposite state; the close equals the opposite entry, so the port emits entries only (reversal).
- 3 % stop of the fill; daily bars with a stop: mark `coarse_bar_stop`. Broker-day bars. FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
