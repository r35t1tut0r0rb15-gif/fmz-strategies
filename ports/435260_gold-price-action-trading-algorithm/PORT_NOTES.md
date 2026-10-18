# #435260 Gold Price Action Trading Algorithm -> `fmz_435260_breakout_20_bracket`

- FMZ source id: 435260 (lineage).
- Source: https://www.fmz.com/strategy/435260 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 16:08:12). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit bracket -> ATR multiple |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the price-unit bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lookback` [20, 40] x `k_atr` [0.2, 1.0]: **4 trials**; the target is 2.5 x the stop.

## Ambiguities resolved

- Price-unit bracket -> ATR multiple; exit re-sends not ported. Mark coarse_bar_stop. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
