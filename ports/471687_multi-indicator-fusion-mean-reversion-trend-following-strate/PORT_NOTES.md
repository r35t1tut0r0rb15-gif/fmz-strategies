# #471687 Multi Indicator Fusion Mean Reversion Trend Following Strategy -> `fmz_471687_macd8_26_5_cross_against_ema30_atr10_stop_reversal`

- FMZ source id: 471687 (lineage).
- Source: https://www.fmz.com/strategy/471687 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 14:30:35). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop at entry |
| 2 | PASS | MACD crossings against the EMA with a wide ATR stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_length` [30, 50] x `atr_mult` [10.0, 3.0]: **4 trials**; the MACD lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
