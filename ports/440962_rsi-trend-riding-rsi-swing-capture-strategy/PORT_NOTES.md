# #440962 趋势顺势RSI波动捕捉策略Trend-Riding-RSI-Swing-Capture-Strategy -> `fmz_440962_volume_sma_macd_cross_rsi_weekday_exit_3h_reversal`

- FMZ source id: 440962 (lineage).
- Source: https://www.fmz.com/strategy/440962 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 10:48:38). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop in the signals |
| 2 | PASS | Volume-confirmed SMA / MACD crossings with RSI limits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Entry qty 1 unit (the equity-based qty is unused), not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_period` [20, 50] x `vol_pct` [50, 25]: **4 trials**; RSI 14, MACD 12 / 26 / 9, stop 1 % / 0.5 %.

## Ambiguities resolved

- Weekday exit block as written; close-based stop from the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
