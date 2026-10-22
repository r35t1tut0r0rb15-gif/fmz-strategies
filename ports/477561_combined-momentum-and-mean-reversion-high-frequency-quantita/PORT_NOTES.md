# #477561 Combined Momentum and Mean Reversion High Frequency Quantitative Strategy -> `fmz_477561_ema50_400_cross_bb20_reentry_reversal`

- FMZ source id: 477561 (lineage).
- Source: https://www.fmz.com/strategy/477561 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-06 13:58:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C234). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings plus Bollinger re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_ema` [400, 200] x `bb_length` [20, 50]: **4 trials**; EMA 50, 2 sd.

## Ambiguities resolved

- Later call wins a two-sided bar. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
