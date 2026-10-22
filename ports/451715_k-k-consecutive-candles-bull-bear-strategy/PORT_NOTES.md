# #451715 K线连续数目牛熊判断策略-K-Consecutive-Candles-Bull-Bear-Strategy -> `fmz_451715_consecutive_close_runs_atr_bracket_giveback_reversal`

- FMZ source id: 451715 (lineage).
- Source: https://www.fmz.com/strategy/451715 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 13:54:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the tick bracket as ATR multiples; the long give-back exit in a loop |
| 2 | PASS | Consecutive-close runs with a profit give-back exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k` [3, 5] x `k_atr` [0.333, 1.0]: **4 trials**; the trail start 0.133 ATR and give-back 50 % fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples (1h ~150); the short give-back names a never-entered id. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
