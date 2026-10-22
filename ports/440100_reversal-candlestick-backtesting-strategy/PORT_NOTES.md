# #440100 Reversal Candlestick Backtesting Strategy -> `fmz_440100_doji_states_short_held`

- FMZ source id: 440100 (lineage).
- Source: https://www.fmz.com/strategy/440100 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-26 16:04:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C131). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested state |
| 2 | ADAPT | Price-unit target / stop -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_frac` [0.00024, 0.01] x `sl_frac` [0.00024, 0.01]: **4 trials**.

## Ambiguities resolved

- Buy state ends every bar as written; short state held until its range. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
