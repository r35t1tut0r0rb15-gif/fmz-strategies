# #444003 1-2-3-形态与-EMAMACD-和第四根蜡烛线延伸的量化交易策略1-2-3-Pattern-Quantitative-Trading-Strategy-with-EMAs-MACD-and-4th-Candle-Extension -> `fmz_444003_123_pattern_ema_macd_counter_bar_exit`

- FMZ source id: 444003 (lineage).
- Source: https://www.fmz.com/strategy/444003 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-03-08 15:03:15). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-bar pattern with trend filters; counter-bar exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [9, 5] x `ema_slow` [20, 50]: **4 trials**; the MACD fixed.

## Ambiguities resolved

- Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
