# #445832 RSI与EMA双重过滤策略RSI-and-EMA-Dual-Filter-Strategy -> `fmz_445832_rsi2_extremes_ema50_200_trend_reversal`

- FMZ source id: 445832 (lineage).
- Source: https://www.fmz.com/strategy/445832 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 15:37:08). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the long's moving stops not ported (mark); the short's wrong-side stop read as a close |
| 2 | PASS | RSI 2 extremes with an EMA trend filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick, trailing and stop inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_len` [200, 100] x `rsi_dn` [10, 5]: **4 trials**; the fast EMA and the upper level fixed.

## Ambiguities resolved

- Long stops pending; shorts out at the next open after the fill (wrong-side stop). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`trailing_stop_pending`
