# #488018 Multi Factor Trend Price Action Strategy with Dynamic Risk Management System -> `fmz_488018_prism_engulf_hammer_volume_adx_atr_bracket_2h_reversal`

- FMZ source id: 488018 (lineage).
- Source: https://www.fmz.com/strategy/488018 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-24 14:11:32). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V44). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | Engulfing / hammer set-ups on volume spikes in trending markets |
| 3 | PASS | Exchange pair in the header only (BNB_USDT). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 1.5] x `tp_atr` [3.0, 4.0]: **4 trials**; EMA 20 / 50, S/R 14, volume x 1.5 / 1.2, ADX 14 > 20.

## Ambiguities resolved

- Strong signals are subsets of the weak ones; repeats re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candlestick_pattern"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
