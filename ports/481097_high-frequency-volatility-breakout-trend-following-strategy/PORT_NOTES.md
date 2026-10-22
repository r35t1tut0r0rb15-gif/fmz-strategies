# #481097 High Frequency Volatility Breakout Trend Following Strategy -> `fmz_481097_bb20_reentry_sma20_side_close_reversal`

- FMZ source id: 481097 (lineage).
- Source: https://www.fmz.com/strategy/481097 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 14:56:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger re-entries on the SMA side with SMA closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [20, 50] x `bb_mult` [2.0, 1.5]: **4 trials**; MA SMA 20.

## Ambiguities resolved

- MA and basis coincide (SMA 20), as written. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
