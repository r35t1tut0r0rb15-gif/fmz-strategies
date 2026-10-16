# #427384 RSI Average Reversion Trading Strategy -> `fmz_427384_rsi_average_swing`

- FMZ source id: 427384 (lineage).
- Source: https://www.fmz.com/strategy/427384 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-20 15:38:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [50, 25] x `long_exit` [0.65, 0.6] x `short_exit` [0.35, 0.4]: **8 trials**; defaults 50 / 0.65 / 0.35 (the source's).

## Ambiguities resolved

- The opposite cross closes and re-enters on one bar (REVERSAL INTENDED).
- Broker-day bars. FREQ = "1D" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
