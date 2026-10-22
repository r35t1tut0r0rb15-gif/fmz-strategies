# #444006 Dynamic Adaptive Trend Trading Strategy -> `fmz_444006_sma10_20_cross_pct_stop_reversal_trail_variant`

- FMZ source id: 444006 (lineage).
- Source: https://www.fmz.com/strategy/444006 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:17:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND444001. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_pct` [0.02, 0.05] x `slow` [20, 50]: **4 trials**; the SMA 10 fixed.

## Ambiguities resolved

- Closes on never-entered ids do nothing; same rules as #444001. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
