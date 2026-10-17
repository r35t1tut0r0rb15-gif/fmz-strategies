# #432361 基于MACD指标的趋势跟踪策略MACD-Trend-Following-Strategy -> `fmz_432361_macd_level_cross_long`

- FMZ source id: 432361 (lineage).
- Source: https://www.fmz.com/strategy/432361 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-16 17:42:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C52). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | ADAPT | Price-unit MACD levels -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432361. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`buy_atr` [-0.2, 0.0] x `sell_atr` [0.1, 0.0]: **4 trials**; MACD 12 / 26, ATR 14 and the 0.05 % stop fixed.

## Ambiguities resolved

- Price-unit levels as ATR multiples (EURUSD reading; the BTC header reading is 0). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
