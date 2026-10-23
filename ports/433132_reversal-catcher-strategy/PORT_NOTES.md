# #433132 Reversal Catcher Strategy -> `fmz_433132_bb_reentry_rsi_cross_counter_trend_eod_reversal`

- FMZ source id: 433132 (lineage).
- Source: https://www.fmz.com/strategy/433132 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-24 16:43:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop and target in the signals |
| 2 | PASS | Bollinger re-entry reversals against the EMA trend with an end-of-day exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = 1 unit, capital 100000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_mult` [1.5, 2.0] x `end_hour` [15, 20]: **4 trials**; BB 20, EMA 21 / 50, RSI 14 at 30 / 70.

## Ambiguities resolved

- Hour read in UTC; shared stop / target levels; end-of-day fill at the next open. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
