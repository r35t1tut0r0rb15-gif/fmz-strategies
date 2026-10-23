# #440526 Multi factor Quantitative Trading Strategy -> `fmz_440526_ema_ribbon_cloud_obv_momentum_4h_long_only`

- FMZ source id: 440526 (lineage).
- Source: https://www.fmz.com/strategy/440526 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 13:55:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA ribbon trend with cloud / momentum triggers and multi-condition exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [21, 10] x `obv_len` [14, 28]: **4 trials**; slow 26, Ichimoku 9 / 26 / 52, RSI 14, EMA ribbon 8 .. 55.

## Ambiguities resolved

- Ichimoku lines as written (SMA-based, undisplaced). Volume = broker tick volume (OBV). Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
