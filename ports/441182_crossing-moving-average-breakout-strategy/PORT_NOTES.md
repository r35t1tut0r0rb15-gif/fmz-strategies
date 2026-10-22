# #441182 Crossing Moving Average Breakout Strategy -> `fmz_441182_stacked_sma_breakout_bar_stop_3bar_exit`

- FMZ source id: 441182 (lineage).
- Source: https://www.fmz.com/strategy/441182 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 15:02:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | Stacked SMAs, channel breakout and bar count |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`candles_back` [10, 20] x `bars_valid` [3, 5]: **4 trials**; SMA 5 / 10 / 20 fixed.

## Ambiguities resolved

- Signal-bar stop re-based on the fill; time exit from the setup bar. Opposite entries cannot occur (entries only from flat). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`coarse_bar_stop`
