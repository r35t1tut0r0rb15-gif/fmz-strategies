# #442523 Dynamic Channel Moving Average Trend Tracking Strategy -> `fmz_442523_noro_bands_trend_pullback_reversal`

- FMZ source id: 442523 (lineage).
- Source: https://www.fmz.com/strategy/442523 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-02-22 15:51:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C157). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel distance bands with a trend state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND441138. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `use_color` [True, False]: **4 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
