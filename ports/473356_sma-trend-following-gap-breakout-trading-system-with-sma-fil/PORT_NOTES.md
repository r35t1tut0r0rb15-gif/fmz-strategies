# #473356 趋势型跳空突破SMA过滤交易系统-Trend-Following-Gap-Breakout-Trading-System-with-SMA-Filter -> `fmz_473356_gap_up_0p1pct_hold10_long`

- FMZ source id: 473356 (lineage).
- Source: https://www.fmz.com/strategy/473356 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-29 15:07:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C217). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Gap-up entries with a fixed hold |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`gap_pct` [0.1, 0.5] x `hold` [10, 5]: **4 trials**; option Long Up Gap, SMA filter off.

## Ambiguities resolved

- Other gap options and the SMA filter not ported (defaults). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`none`
