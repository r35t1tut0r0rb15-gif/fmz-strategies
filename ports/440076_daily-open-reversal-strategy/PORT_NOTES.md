# #440076 Daily Open Reversal Strategy -> `fmz_440076_daily_candle_fade_tick_bracket`

- FMZ source id: 440076 (lineage).
- Source: https://www.fmz.com/strategy/440076 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 14:35:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C130). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit range -> fraction; tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the pip inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_sl` [0.1, 2.0]: **2 trials**; target = 0.2 x stop; range 2.4e-7 of the close fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples; range as a fraction. Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`coarse_bar_stop`
