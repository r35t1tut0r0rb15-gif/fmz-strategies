# #442640 Quadruple Crossing Strategy -> `fmz_442640_quadruple_cross_confluence_dip_entries_1h_long_only`

- FMZ source id: 442640 (lineage).
- Source: https://www.fmz.com/strategy/442640 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 14:20:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Trend-pullback momentum confluence or deep-dip entries with mirrored exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10 % of equity, capital 100000, commission 0.1 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_k` [2.5, 2.0] x `ema_long` [200, 100]: **4 trials**; EMA 20, RSI 14, MACD 12 / 26 / 9.

## Ambiguities resolved

- Conditions as written. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
