# #436634 A DMI Stochastic Trading Strategy with Dynamic Stop loss -> `fmz_436634_dmi_stoch_extreme_close_stop`

- FMZ source id: 436634 (lineage).
- Source: https://www.fmz.com/strategy/436634 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-26 14:30:23). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C93). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop level fixed at entry |
| 2 | ADAPT | Stop level -> distance fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [14, 10] x `adx_threshold` [25, 20]: **4 trials**; %K length 14 and the 20 / 80 levels fixed.

## Ambiguities resolved

- Stop = running extreme close of the loaded history, as a distance fraction. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_filter"`.

## Marks

`coarse_bar_stop`
