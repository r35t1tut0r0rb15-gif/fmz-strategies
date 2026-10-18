# #435948 基于一目均线系统的BTC交易策略Ichimoku-Kinko-Hyo-Based-BTC-Trading-Strategy -> `fmz_435948_ichimoku_votes_long`

- FMZ source id: 435948 (lineage).
- Source: https://www.fmz.com/strategy/435948 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-12-20 13:34:08). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Ichimoku lines and an RSI rebound |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed order size, commission and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND434984. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kijun_lag` [6, 4] x `kijun_len` [26, 20]: **4 trials**; Tenkan 9, span B 52 and the RSI settings fixed.

## Ambiguities resolved

- Undisplaced spans; counters in a loop. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
