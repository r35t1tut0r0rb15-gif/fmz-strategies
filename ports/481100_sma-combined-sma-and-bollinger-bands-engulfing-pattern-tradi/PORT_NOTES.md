# #481100 基于SMA和布林带的吞没形态指标组合交易策略-Combined-SMA-and-Bollinger-Bands-Engulfing-Pattern-Trading-Strategy -> `fmz_481100_engulf_style_sma200_bb14_basis_2r_bracket_reversal`

- FMZ source id: 481100 (lineage).
- Source: https://www.fmz.com/strategy/481100 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-08 15:06:49). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C241). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar candle bracket as fractions of the fill |
| 2 | PASS | Engulfing-style candles with SMA 200 / BB basis filters and a 2 R bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rr` [2.0, 1.0] x `bb_length` [14, 20]: **4 trials**; SMA 200.

## Ambiguities resolved

- Repeat-signal re-sends not followed. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
