# #452364 Trend Following Average True Range Trailing Stop Strategy -> `fmz_452364_clamped_atr_line_cross_reversal`

- FMZ source id: 452364 (lineage).
- Source: https://www.fmz.com/strategy/452364 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-24 18:12:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C188). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR-line crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [3.0, 2.0] x `atr_len` [10, 14]: **4 trials**.

## Ambiguities resolved

- The clamped line as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
