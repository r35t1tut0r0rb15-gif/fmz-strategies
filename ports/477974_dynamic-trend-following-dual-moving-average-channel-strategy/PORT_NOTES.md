# #477974 Dynamic Trend Following Dual Moving Average Channel Strategy with Risk Management System -> `fmz_477974_ma_channel_5bar_persistence_long`

- FMZ source id: 477974 (lineage).
- Source: https://www.fmz.com/strategy/477974 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 16:26:56). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C238). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel persistence entries with a channel exit and a deep high-water stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`count` [5, 3] x `stop_pct` [0.25, 0.05]: **4 trials**; upper SMA 10, lower SMA 8.

## Ambiguities resolved

- Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
