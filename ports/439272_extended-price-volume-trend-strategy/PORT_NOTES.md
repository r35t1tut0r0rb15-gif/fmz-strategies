# #439272 Extended Price Volume Trend Strategy -> `fmz_439272_extended_pvt_level_cross_ladder_tp_reversal`

- FMZ source id: 439272 (lineage).
- Source: https://www.fmz.com/strategy/439272 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-18 16:32:28). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-volume-trend pivot level crossings with ladder take-profits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [200, 100] x `tp1` [10, 5]: **4 trials**; tp2 / tp3 = 2 / 3 x tp1.

## Ambiguities resolved

- VTY from crossings either way; closes act only on unchanged positions. Volume = broker tick volume (PVT). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_flow"`.

## Marks

`none`
