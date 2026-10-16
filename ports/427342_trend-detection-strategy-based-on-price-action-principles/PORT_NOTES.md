# #427342 Trend Detection Strategy Based on Price Action Principles -> `fmz_427342_close_position_trend_detect`

- FMZ source id: 427342 (lineage).
- Source: https://www.fmz.com/strategy/427342 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-20 11:11:46). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Shares of candle types. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [34, 21, 55] x `ema_smooth` [5, 3]: **6 trials**; defaults 34 / 5 (the source's).

## Ambiguities resolved

- The count covers the 34 bars before the current one.
- `num / len * 100` read as a real division. **Decision owed (minor):** if Pine v2 divides two integers as integers, the share is only 0 or 100 and the crosses become rare; the port would then need a variant.
- REVERSAL INTENDED. FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
