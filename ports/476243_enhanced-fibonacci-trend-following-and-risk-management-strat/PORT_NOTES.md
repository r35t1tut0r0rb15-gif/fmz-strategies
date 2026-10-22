# #476243 Enhanced Fibonacci Trend Following and Risk Management Strategy -> `fmz_476243_fib065_range_cross_sma181_side_reversal`

- FMZ source id: 476243 (lineage).
- Source: https://www.fmz.com/strategy/476243 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 14:10:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C230). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; per-bar bracket described (pending) |
| 2 | PASS | Range-retracement crossings with an SMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The ATR bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [38, 20] x `sma_length` [181, 100]: **4 trials**; the 0.65 level fixed; the per-bar bracket pending.

## Ambiguities resolved

- The previous close is compared with the current level, as written.
- Per-bar ATR bracket from the latest close kept pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`trailing_stop_pending`
