# #427928 Multiple Timeframe Filtered Trend Following Strategy -> `fmz_427928_rsi2_extremes_sma200_side_tick_stop_reversal`

- FMZ source id: 427928 (lineage).
- Source: https://www.fmz.com/strategy/427928 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 20:36:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; RSI exits and a fixed-fraction stop (approximation stated) |
| 2 | PASS | RSI 2 mean reversion with an SMA 200 side filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.019, 0.01] x `rsi_low` [20.0, 10.0]: **4 trials**; RSI 2 high 80, SMA 200, EMA 20.

## Ambiguities resolved

- 5000 ticks read as 0.019 of the fill at the source's BTC prices (approximation). Volume only plotted.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
