# #443092 Dual Timeframe Trend Following Strategy -> `fmz_443092_ema20_50_order_reversal_pending_bracket`

- FMZ source id: 443092 (lineage).
- Source: https://www.fmz.com/strategy/443092 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 10:58:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent bracket pending |
| 2 | PASS | EMA order |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND442953. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Same-time-frame request; the short count dropped; bracket pending. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`trailing_stop_pending`
