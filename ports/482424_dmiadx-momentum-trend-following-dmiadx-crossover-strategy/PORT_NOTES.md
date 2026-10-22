# #482424 动量趋势跟踪指标DMIADX交叉策略-Momentum-Trend-Following-DMIADX-Crossover-Strategy -> `fmz_482424_di14_cross_adx25_pct_bracket_reversal`

- FMZ source id: 482424 (lineage).
- Source: https://www.fmz.com/strategy/482424 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-02-18 13:47:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C243). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; avg-price bracket as fractions of the fill |
| 2 | PASS | DI crossings with an ADX filter and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_threshold` [25.0, 20.0] x `tp_pct` [0.02, 0.04]: **4 trials**; DMI 14 / 14, stop 1 %.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`coarse_bar_stop`
