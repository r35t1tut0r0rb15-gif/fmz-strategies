# #439362 基于动态止损和目标获利的EMA多次成本加权平均成本策略EMA-Multi-DCA-Strategy-with-Trailing-Stop-Loss-and-Profit-Target -> `fmz_439362_ema_band_touch_atr_close_long`

- FMZ source id: 439362 (lineage).
- Source: https://www.fmz.com/strategy/439362 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-19 15:16:53). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C120). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Price-unit ATR threshold -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The per-buy amount stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_frac` [0.00024, 0.03] x `band` [0.01, 0.005]: **4 trials**; the EMA set, ATR 20 and the limit 3000 fixed.

## Ambiguities resolved

- ATR threshold as a fraction of the close; exits on an unused id never sent. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
