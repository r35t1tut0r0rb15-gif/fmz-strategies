# #433968 Momentum Dual Moving Average Trading Strategy -> `fmz_433968_noro_price_channel_v12`

- FMZ source id: 433968 (lineage).
- Source: https://www.fmz.com/strategy/433968 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-01 18:13:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C64). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel position, candle colours, RSI levels and body ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital % lot stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430009. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pch` [30, 60] x `rsi_limit` [25, 15]: **4 trials**; the short RSI level is 100 - rsi_limit.

## Ambiguities resolved

- Trend line plot-only as written; per-bar order resolution stated. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
