# #451722 Price and Volume Breakout Buy Strategy -> `fmz_451722_price_volume_60bar_breakout_sma200_long_only`

- FMZ source id: 451722 (lineage).
- Source: https://www.fmz.com/strategy/451722 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 14:54:13). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price and volume range breakouts above the long trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 70 % of equity, capital 10000, commission 0.01 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`breakout` [60, 20] x `trend_len` [200, 100]: **4 trials**; volume breakout = price breakout length.

## Ambiguities resolved

- Five closes against the current SMA 200. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
