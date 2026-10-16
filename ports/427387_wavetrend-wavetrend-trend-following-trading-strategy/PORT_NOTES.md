# #427387 WaveTrend Trend Following Trading Strategy -> `fmz_427387_noro_wavetrend`

- FMZ source id: 427387 (lineage).
- Source: https://www.fmz.com/strategy/427387 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 15:50:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Normalised channel index. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`channel` [10, 20] x `average` [21, 40] x `only_long` [True, False]: **8 trials**; defaults 10 / 21 / True (the source's).

## Ambiguities resolved

- Only-long: the qty-0 short entry closes the long (Noro idiom). With both sides the turns reverse.
- FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "wavetrend_oscillator"`.

## Marks

`none`
