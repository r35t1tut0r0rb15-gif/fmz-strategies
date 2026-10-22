# #458133 Multi Period Moving Average Crossover Trend Following Strategy -> `fmz_458133_sma20_50_cross_sma200_filter_signal_bar_stop_reversal`

- FMZ source id: 458133 (lineage).
- Source: https://www.fmz.com/strategy/458133 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 10:54:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C201). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the stop levels as close tests |
| 2 | PASS | SMA crossings with a long-average filter and signal-bar stops |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma1` [20, 10] x `ma2` [50, 30] x `ma4` [200, 100]: **8 trials**; the MA type SMA fixed.

## Ambiguities resolved

- No bar size in the source (bar_size_pending); exits sent while flat not carried to a later entry. REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
