# #439748 Money Flow Index 5 Minute Strategy Across Time and Space -> `fmz_439748_mfi3_extreme_strong_candle_sma80_short_daystop_1m_reversal`

- FMZ source id: 439748 (lineage).
- Source: https://www.fmz.com/strategy/439748 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:46:55). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; short-only bracket fixed at the signal bar |
| 2 | PASS | MFI extremes followed by strong candles with a trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [80, 40] x `body` [0.5, 0.7]: **4 trials**; MFI 3, stop increment 3 %, R:R 2.2.

## Ambiguities resolved

- Shared exit id: short-only bracket fixed at the signal bar. Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mfi_threshold"`.

## Marks

`trailing_stop_pending`
