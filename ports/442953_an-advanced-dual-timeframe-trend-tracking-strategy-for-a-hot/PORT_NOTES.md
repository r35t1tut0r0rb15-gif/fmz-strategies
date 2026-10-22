# #442953 An Advanced Dual Timeframe Trend Tracking Strategy for a Hot Stock -> `fmz_442953_daily_hourly_ema20_50_agreement_reversal`

- FMZ source id: 442953 (lineage).
- Source: https://www.fmz.com/strategy/442953 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-27 16:01:41). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C163). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the hourly values end with the day; the re-sent bracket pending |
| 2 | PASS | Daily and hourly EMA agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND442953. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials** (the same lengths on both time frames, as written).

## Ambiguities resolved

- Hourly values as the day's last bar; 2023 window and the short count dropped; bracket pending. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_timeframe_ma"`.

## Marks

`trailing_stop_pending`
