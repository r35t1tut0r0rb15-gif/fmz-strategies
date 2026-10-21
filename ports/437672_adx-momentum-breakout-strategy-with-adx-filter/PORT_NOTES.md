# #437672 顺势突破ADX过滤交易策略Momentum-Breakout-Strategy-with-ADX-Filter -> `fmz_437672_upper_band_reentry_adx_long`

- FMZ source id: 437672 (lineage).
- Source: https://www.fmz.com/strategy/437672 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 17:12:30). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [33, 20] x `k_atr` [0.67, 1.5]: **4 trials**; 2 sigma, ADX 4 / 8 / 15 and the 2:1 target fixed.

## Ambiguities resolved

- Entry named ShortEntry is a long as written; tick bracket -> ATR multiples. Long only. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
