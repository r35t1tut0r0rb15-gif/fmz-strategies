# #437378 Trend Following Strategy Based on Dynamic Moving Average -> `fmz_437378_alma_high_low_baseline`

- FMZ source id: 437378 (lineage).
- Source: https://www.fmz.com/strategy/437378 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-02 10:44:53). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C100). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close against average baselines |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`baseline` [55, 30] x `sigma` [10.0, 6.0]: **4 trials**; ALMA, offset 0.85, source ohlc4 fixed.

## Ambiguities resolved

- Same-resolution security; VWMA type left out. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`none`
