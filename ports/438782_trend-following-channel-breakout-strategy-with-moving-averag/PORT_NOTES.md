# #438782 Trend Following Channel Breakout Strategy with Moving Average and Trailing Stop -> `fmz_438782_gssl_channel_flip_atr_trail`

- FMZ source id: 438782 (lineage).
- Source: https://www.fmz.com/strategy/438782 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-01-15 12:25:26). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C112). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; house trail |
| 2 | ADAPT | Tick stop and trail -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The tick inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.086, 1.0] x `k_trail` [0.0003, 0.5]: **4 trials**; Lb 10, SMA, ATR 14 and activation 0.00036 fixed.

## Ambiguities resolved

- Tick stop / trail -> ATR multiples (reading and a wider pair). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`coarse_bar_stop, trailing_stop`
