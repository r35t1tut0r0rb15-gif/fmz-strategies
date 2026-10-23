# #452354 Buy and Sell Volume Heatmap with Real Time Price Strategy -> `fmz_452354_ema_vwap_volume_first_bar_two_red_short_1h_reversal`

- FMZ source id: 452354 (lineage).
- Source: https://www.fmz.com/strategy/452354 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 17:16:58). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | First bars of EMA / VWAP / volume momentum, two-red-candle shorts |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `vol_len` [20, 50]: **4 trials**; EMA 20.

## Ambiguities resolved

- signal_occurred blocks the next bar; later call wins. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
