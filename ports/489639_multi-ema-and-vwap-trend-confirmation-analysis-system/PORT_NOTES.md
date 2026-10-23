# #489639 Multi EMA and VWAP Trend Confirmation Analysis System -> `fmz_489639_ema8_50_cross_vs_session_vwap_0730_1430_1h_reversal`

- FMZ source id: 489639 (lineage).
- Source: https://www.fmz.com/strategy/489639 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-07 11:45:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings in the direction of the EMA 50 against the VWAP |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 13] x `slow` [50, 34]: **4 trials**; session VWAP of close, 07:30-14:30 UTC.

## Ambiguities resolved

- Session read in UTC, bar-open rule. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
