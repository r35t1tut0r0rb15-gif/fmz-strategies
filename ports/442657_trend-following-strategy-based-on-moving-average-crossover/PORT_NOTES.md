# #442657 Trend Following Strategy Based on Moving Average Crossover -> `fmz_442657_sma50_200_cross_long_bracket_short_one_bar`

- FMZ source id: 442657 (lineage).
- Source: https://www.fmz.com/strategy/442657 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 15:14:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_len` [50, 20] x `long_len` [200, 100]: **4 trials**; the bracket fractions fixed.

## Ambiguities resolved

- Long bracket from the fill bar; the short closes after its first bar (wrong-side levels). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
