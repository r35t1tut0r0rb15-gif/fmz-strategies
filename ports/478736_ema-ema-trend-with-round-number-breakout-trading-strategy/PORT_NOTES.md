# #478736 EMA趋势结合轮回位突破交易策略-EMA-Trend-with-Round-Number-Breakout-Trading-Strategy -> `fmz_478736_engulf_style_ema20_side_reversal`

- FMZ source id: 478736 (lineage).
- Source: https://www.fmz.com/strategy/478736 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-17 16:17:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C240). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | Engulfing-style closes on the EMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 200 % of equity stored, not ported; the bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [20, 50]: **2 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`trailing_stop_pending`
