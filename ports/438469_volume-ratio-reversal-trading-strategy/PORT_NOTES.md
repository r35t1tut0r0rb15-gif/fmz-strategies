# #438469 Volume Ratio Reversal Trading Strategy -> `fmz_438469_volume_ratio_spike_direction_1h_reversal`

- FMZ source id: 438469 (lineage).
- Source: https://www.fmz.com/strategy/438469 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 12:08:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Volume spikes in the bar's direction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `threshold` [3.0, 2.0]: **4 trials**; direction over 1 bar.

## Ambiguities resolved

- A flat close counts as down. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_filter"`.

## Marks

`none`
