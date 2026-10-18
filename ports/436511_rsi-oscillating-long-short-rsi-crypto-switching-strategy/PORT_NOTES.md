# #436511 震荡多空RSI换币策略Oscillating-Long-Short-RSI-Crypto-Switching-Strategy -> `fmz_436511_ichimoku_ha_rsi`

- FMZ source id: 436511 (lineage).
- Source: https://www.fmz.com/strategy/436511 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-25 13:49:48). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C90). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Ichimoku on Heikin-Ashi closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ts_bars` [20, 10] x `ks_bars` [50, 30]: **4 trials**; Senkou B 120 and the offsets fixed.

## Ambiguities resolved

- Bearish test uses rs under 50 as written. REVERSAL INTENDED. FREQ = "3min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
