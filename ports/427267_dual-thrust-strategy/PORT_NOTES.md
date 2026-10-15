# #427267 Dual Thrust Strategy -> `fmz_427267_dual_thrust`

- FMZ source id: 427267 (lineage).
- Source: https://www.fmz.com/strategy/427267 (PineScript v3, author ChaoZhang,
  FMZ last modified 2023-09-19 16:27:12). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C3). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 4-hour and daily values only once those bars have ended (lookahead_off). |
| 2 | PASS | Range is a price difference scaled by k1 / k2. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | qty 1 and initial capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k1` [0.67, 0.4] x `k2` [0.62, 0.4] x `length` [20, 10]: **8 trials**; defaults 0.67 / 0.62 / 20 (the source's); TimeFrame 4 h fixed.

## Ambiguities resolved

- `security(..., 'D', open, lookahead_off)` on history = the open of the last completed broker day (yesterday), not today's. Ported as the script behaves. **Decision owed:** a textbook version on today's open (known at the day's start) would be a separate module.
- Higher bars end at fixed clock times (4-hour UTC grid; broker day at 17:00 New York), so a 10-minute bar sees every block / day that ended at or before its own close.
- REVERSAL INTENDED. FREQ = "10min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
