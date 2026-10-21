# #438933 Price Channel Breakout Strategy -> `fmz_438933_noro_price_channel_pullback`

- FMZ source id: 438933 (lineage).
- Source: https://www.fmz.com/strategy/438933 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-16 14:22:57). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C114). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Channel centre, bar colours and body size |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pch` [30, 60] x `body_ratio` [0.5, 1.0]: **4 trials**; body SMA 10 fixed.

## Ambiguities resolved

- close_all after the entries ends the bar flat (as #430380). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
