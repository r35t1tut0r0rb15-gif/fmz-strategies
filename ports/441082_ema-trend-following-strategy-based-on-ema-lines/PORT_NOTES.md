# #441082 基于EMA平均线的趋势跟踪策略Trend-Following-Strategy-Based-on-EMA-Lines -> `fmz_441082_ema20_59_always_in_tick_stop`

- FMZ source id: 441082 (lineage).
- Source: https://www.fmz.com/strategy/441082 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-05 14:21:18). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C146). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | ADAPT | Tick stop -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema2` [20, 40] x `ema3` [59, 100]: **4 trials**; the stop multiple fixed.

## Ambiguities resolved

- Tick stop as an ATR multiple (1.5 at the 45-minute reading). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
