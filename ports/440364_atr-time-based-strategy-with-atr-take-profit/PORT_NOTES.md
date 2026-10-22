# #440364 基于时间和ATR指标的止损止盈策略Time-based-Strategy-with-ATR-Take-Profit -> `fmz_440364_0700_short_5min_atr_target`

- FMZ source id: 440364 (lineage).
- Source: https://www.fmz.com/strategy/440364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 16:13:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C133). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry; the 5-minute value ends with the chart bar |
| 2 | PASS | Time of day and a 5-minute ATR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND440364. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trade_hour` [7, 13] x `atr_len` [14, 28]: **4 trials**; 5-minute ATR bars fixed.

## Ambiguities resolved

- Hour read on the UTC bar open; 5-minute ATR from the last 5-minute bar; later target moves not followed. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "calendar_seasonal"`.

## Marks

`none`
