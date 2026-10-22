# #442652 Rainbow Oscillator Trading Strategy -> `fmz_442652_rainbow_oscillator_cross_pct_bracket`

- FMZ source id: 442652 (lineage).
- Source: https://www.fmz.com/strategy/442652 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:57:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed from the fill |
| 2 | PASS | Blended oscillator crossings with a trend filter |
| 3 | PASS | No exchange header. |
| 4 | DONE | Margin settings and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_period` [16, 10] x `slow_period` [22, 40]: **4 trials**; the weights, smoothing and bracket fixed.

## Ambiguities resolved

- Bracket from the fill bar as fixed fractions. REVERSAL INTENDED. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`bar_size_pending`
