# #489736 Multi Moving Average Trend Filter Crossover Quantitative Trading Strategy -> `fmz_489736_ema17_31_cross_vwap_sma69_ema8_9_exit_1h_reversal`

- FMZ source id: 489736 (lineage).
- Source: https://www.fmz.com/strategy/489736 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-04-08 10:18:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings above / below the VWAP and SMA 69 with faster EMA exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`entry_fast` [17, 12] x `entry_slow` [31, 26]: **4 trials**; SMA 69, session VWAP of hlc3, exits EMA 8 / 9.

## Ambiguities resolved

- Flags followed as written (rare entry-and-exit bar). Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
