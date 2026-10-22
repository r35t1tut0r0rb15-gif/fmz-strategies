# #442618 Triple Dynamic Moving Average Trend Tracking Strategy -> `fmz_442618_mcginley_15m_1h_cross_4h_trend`

- FMZ source id: 442618 (lineage).
- Source: https://www.fmz.com/strategy/442618 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 12:07:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C158). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 4-hour values from completed bars, 15-minute values ending with the bar |
| 2 | PASS | Multi-time-frame McGinley crossings with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity quantity, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `length3` [50, 100]: **4 trials** (one length for the 15-minute and 1-hour lines, as their defaults agree).

## Ambiguities resolved

- 15-minute value ends with the hour; 4-hour value from the last completed block. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`none`
