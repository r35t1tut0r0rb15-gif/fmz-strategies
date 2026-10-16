# #428812 Breakout Day Trading Strategy -> `fmz_428812_morning_sma2_breakout`

- FMZ source id: 428812 (lineage).
- Source: https://www.fmz.com/strategy/428812 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-09 16:56:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; clock-time exits as signals. |
| 2 | ADAPT | The tick stop -> an ATR multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out strategy(), the risk-% size and the stop quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.05, 0.5] x `trend_length` [200, 100]: **4 trials**; SMA 2 and the UTC windows fixed.

## Ambiguities resolved

- Exchange time taken as UTC; a bar is in a window by its open time. Time exits are signals.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
