# #435158 Ichimoku Trading Strategy With Money Management -> `fmz_435158_ichimoku_entry_price_exits_long`

- FMZ source id: 435158 (lineage).
- Source: https://www.fmz.com/strategy/435158 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 17:32:08). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes against the fill price |
| 2 | PASS | Ichimoku lines, ATR stretch limits and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gain_exit` [1.30, 1.15] x `loss_exit` [0.93, 0.85]: **4 trials**; the Ichimoku periods and ATR 14 fixed.

## Ambiguities resolved

- Exits on closes against the fill price. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
