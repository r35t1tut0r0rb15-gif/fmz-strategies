# #483038 多重技术指标动态交叉趋势识别策略-Dynamic-Multi-Indicator-Trend-Recognition-Strategy-with-Triple-Sync-Analysis -> `fmz_483038_snake_line_range_cross_reversal`

- FMZ source id: 483038 (lineage).
- Source: https://www.fmz.com/strategy/483038 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 10:31:53). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillators and their own rolling range. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 21] x `dyn_len` [100, 50]: **4 trials**; defaults 14 / 100 (the source's); the 20 % / 80 % levels fixed.

## Ambiguities resolved

- The DMI is the source's own simplified one (no up / down comparison), as written. `ta.cci` with mean absolute
  deviation.
- close + entry is a reversal: only entries emitted; a long and a short on one bar: the later short wins.
- REVERSAL INTENDED; no exits or stops. Broker days stamped with their first minute (as #430984). FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_cross"`.

## Marks

`none`
