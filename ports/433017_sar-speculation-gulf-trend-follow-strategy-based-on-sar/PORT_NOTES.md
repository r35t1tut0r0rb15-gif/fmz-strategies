# #433017 基于-SAR-的趋势追踪型量化策略Speculation-Gulf-Trend-Follow-Strategy-Based-on-SAR -> `fmz_433017_sar_flip_ema_squeeze`

- FMZ source id: 433017 (lineage).
- Source: https://www.fmz.com/strategy/433017 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-23 16:26:17). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C57). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR position, averages, body stdev and a momentum slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the bot alert messages are not trading rules). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [100, 200] x `n_bars` [4, 8]: **4 trials**; SAR 0.02 / 0.02 / 0.2, volatility 100 and KC 20 fixed.

## Ambiguities resolved

- Default filters only (squeeze slope, not the squeeze flags); exits by SAR flip. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`none`
