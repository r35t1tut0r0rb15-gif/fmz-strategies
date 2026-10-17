# #431410 多时间框架趋势跟踪DI策略Dual-Timeframe-DI-Trend-Following-Strategy -> `fmz_431410_di_trend_ratchet_long`

- FMZ source id: 431410 (lineage).
- Source: https://www.fmz.com/strategy/431410 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-07 16:31:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exit |
| 2 | PASS | DI comparison and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 5 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_len` [14, 28] x `tsl_mult` [2.0, 3.0]: **4 trials**; ATR 14 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the resting ratchet stop order; the close-checked exit ported. Long only.
  FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "directional_movement"`.

## Marks

`trailing_stop_pending`
