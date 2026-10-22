# #473371 基于多区域SMC理论的智能趋势跟踪策略Multi-Zone-SMC-Theory-Based-Intelligent-Trend-Following-Strategy -> `fmz_473371_swing8_equilibrium_zones_sma50_reversal`

- FMZ source id: 473371 (lineage).
- Source: https://www.fmz.com/strategy/473371 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:38:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Swing-range zones with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing_len` [8, 16] x `sma_len` [50, 100]: **4 trials**; the order-block length feeds nothing.

## Ambiguities resolved

- A tie with an earlier high / low counts as a new swing (highestbars offset 0). REVERSAL INTENDED.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_levels"`.

## Marks

`none`
