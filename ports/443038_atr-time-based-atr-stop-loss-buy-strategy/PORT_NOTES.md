# #443038 基于时间和ATR止损定时买入策略Time-based-ATR-Stop-Loss-Buy-Strategy -> `fmz_443038_daily_0700_buy_5m_atr_target_long`

- FMZ source id: 443038 (lineage).
- Source: https://www.fmz.com/strategy/443038 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-28 17:36:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C165). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry; the 5-minute value ends with the bar |
| 2 | PASS | Time-of-day entry with an ATR target |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND440364. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trade_hour` [7, 13] x `atr_length` [14, 28]: **4 trials**.

## Ambiguities resolved

- Target from the signal bar's 5-minute ATR; no stop. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
