# #483043 Advanced Opportunity Space Oscillator Strategy A Quantitative Trading System Based on Fair Value Gaps -> `fmz_483043_fvg_gap_volume_or_size_confirmed_1h_reversal`

- FMZ source id: 483043 (lineage).
- Source: https://www.fmz.com/strategy/483043 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-24 14:55:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Fair-value gaps confirmed by volume or gap size |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lnt` [50, 100] x `size_mult` [1.5, 2.0]: **4 trials**; volume SMA 10.

## Ambiguities resolved

- Bearish gap-size test uses a negative difference, as written. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "gap"`.

## Marks

`none`
