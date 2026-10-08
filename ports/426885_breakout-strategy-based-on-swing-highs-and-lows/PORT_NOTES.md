# #426885 Breakout Strategy Based on Swing Highs and Lows -> `fmz_426885_jetzgiantz_swing_reversal`

- Source: https://www.fmz.com/strategy/426885 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-15 11:47:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick distances -> ATR(14) multiples at the signal bar. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.25, 0.5, 1.0]: **3 trials**, target 10 x the stop (the source's ratio); 0.25 is the smallest step (10 ticks is a small fraction of a 4h ATR).

## Ambiguities resolved

- Kept as written: the sell rule's close > open[1] (decision owed).
- Criterion 2 (ADAPT): 10 / 100 ticks -> sl_atr x ATR(14) at the signal bar, target 10x.
- Entries only from flat (strategy.order when flat): simulate() mirrors stop and target. Month / year filter dropped.
- Stops on 4h bars: coarse_bar_stop.

## FAMILY (proposed, user to confirm)

`FAMILY = "pivot_reversal"`.

## Marks (2026-10-07)

`coarse_bar_stop`
