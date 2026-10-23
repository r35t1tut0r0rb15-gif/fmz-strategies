# #426389 Cryptocurrency RSI Curve Tracking Strategy -> `fmz_426389_volume_weighted_rsi100_rvi_state_long_pct_bracket`

- FMZ source id: 426389 (lineage).
- Source: https://www.fmz.com/strategy/426389 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-11 17:24:59). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the signal close |
| 2 | PASS | Volume-weighted RSI with a volatility-direction state |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 2.5 / open x risk / 100, 100 % of equity, capital 1000, commission 0.03 % stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [100, 50] x `sl` [0.2, 0.05]: **4 trials**; zones 49 / 50, TP 1.0.

## Ambiguities resolved

- Bracket fixed at the signal close (100 % / 20 %). Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`trailing_stop_pending`
