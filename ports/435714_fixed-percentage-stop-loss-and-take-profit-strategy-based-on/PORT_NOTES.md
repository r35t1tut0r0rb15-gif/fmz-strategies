# #435714 Fixed Percentage Stop Loss and Take Profit Strategy Based on Moving Averages -> `fmz_435714_ema_5_32_cross_percent_bracket`

- FMZ source id: 435714 (lineage).
- Source: https://www.fmz.com/strategy/435714 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 11:30:39). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C80). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Average cross and a percent bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_per` [0.05, 0.03] x `take_per` [0.10, 0.06]: **4 trials**; EMA 5 / 32 fixed.

## Ambiguities resolved

- Percent bracket from the fill. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
