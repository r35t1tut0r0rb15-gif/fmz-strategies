# #435957 Bollinger Band based Price Action Strategy -> `fmz_435957_bollinger_reversal_candle_bracket`

- FMZ source id: 435957 (lineage).
- Source: https://www.fmz.com/strategy/435957 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 14:03:52). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C83). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_atr` [0.0001, 0.5] x `b_sma` [21, 34]: **4 trials**; 2.1 sd fixed; the target is twice the stop.

## Ambiguities resolved

- Tick bracket -> ATR multiple. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`coarse_bar_stop`
