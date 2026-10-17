# #431413 基于KST指标和EMA指标的交易策略KST-EMA-Momentum-Trend-Following-Strategy -> `fmz_431413_kst_ema_trail`

- FMZ source id: 431413 (lineage).
- Source: https://www.fmz.com/strategy/431413 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-07 16:36:21). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the trail is a house stop |
| 2 | PASS | KST, an EMA and a percentage trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [1.0, 3.0] x `ema_len` [50, 100]: **4 trials**; the KST lengths and signal 9 fixed.

## Ambiguities resolved

- House percent trail on closes. Marks trailing_stop, coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`trailing_stop, coarse_bar_stop`
