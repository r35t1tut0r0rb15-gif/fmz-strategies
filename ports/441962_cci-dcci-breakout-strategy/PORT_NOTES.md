# #441962 动态CCI突破策略DCCI-Breakout-Strategy -> `fmz_441962_cci16_100_reentry_wma_side_atr_bracket`

- FMZ source id: 441962 (lineage).
- Source: https://www.fmz.com/strategy/441962 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-18 10:13:21). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from signal-bar data (approximation stated) |
| 2 | ADAPT | Fill-bar ATR stop -> signal-bar ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND438012. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_len` [16, 20] x `atr_mult` [10.0, 5.0]: **4 trials**; WMA 5 and RR 1.5 fixed.

## Ambiguities resolved

- ATR stop from the signal bar instead of the fill bar's ohlc4 (stated). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`coarse_bar_stop`
