# #437789 The Momentum Driven Triple Confirmation Trend Following Strategy -> `fmz_437789_mom_rsi_supertrend_ema_trail`

- FMZ source id: 437789 (lineage).
- Source: https://www.fmz.com/strategy/437789 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-05 15:46:21). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C106). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the beyond-the-market stop read as a close at the next open |
| 2 | PASS | Momentum RSI, SuperTrend and an EMA trail line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed 50000 per position and the unused static bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND437789. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `mom_rsi_val` [60, 50]: **4 trials**; momentum / RSI 10, ATR 10, EMA 12 and 1 % fixed.

## Ambiguities resolved

- SuperTrend stop beyond the market read as a next-open close; Version 2 off. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
