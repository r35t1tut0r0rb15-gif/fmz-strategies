# #458140 Multi Period Dynamic Channel Crossover Strategy -> `fmz_458140_donchian_mid_base_cross_displaced_spans_reversal`

- FMZ source id: 458140 (lineage).
- Source: https://www.fmz.com/strategy/458140 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-30 11:59:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C202). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel mid-line crossings with displaced spans |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`conversion` [5, 9] x `base` [51, 26] x `displace` [21, 26]: **8 trials**; the span-2 length 68 fixed.

## Ambiguities resolved

- Same rules as #458067 (no bracket). REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
