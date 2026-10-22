# #440994 Momentum Price Climbing Crypto Currency Strategy -> `fmz_440994_range_mid_vortex_cross_long_bracket`

- FMZ source id: 440994 (lineage).
- Source: https://www.fmz.com/strategy/440994 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-04 15:38:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C143). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket from the close -> fixed fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`candles` [60, 30] x `vortex_len` [14, 28]: **4 trials**; target and stop 0.1 fixed.

## Ambiguities resolved

- Tick bracket as fixed fractions. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
