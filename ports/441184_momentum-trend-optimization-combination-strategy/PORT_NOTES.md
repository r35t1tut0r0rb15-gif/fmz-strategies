# #441184 Momentum Trend Optimization Combination Strategy -> `fmz_441184_ema2_slope_sma8_cross_volume_trend_long_only`

- FMZ source id: 441184 (lineage).
- Source: https://www.fmz.com/strategy/441184 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 15:11:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed stop and target from the fill |
| 2 | PASS | Fast EMA crossings of a slope-adjusted SMA with trend and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity x 1 % x 2 / ATR, 100 % of equity default, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [35, 50] x `tp` [0.25, 0.1]: **4 trials**; stop 50 %, EMA 2, SMA 8 slope line.

## Ambiguities resolved

- Exit on the next same-direction cross as written; script flag kept after stops. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
