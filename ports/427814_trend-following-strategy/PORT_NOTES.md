# #427814 Trend Following Strategy -> `fmz_427814_noro_trendmaster`

- FMZ source id: 427814 (lineage).
- Source: https://www.fmz.com/strategy/427814 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-25 17:50:11). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel of closes, RSI levels, body ratio. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity quantity and switch quantities stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len` [21, 10, 50, 100]: **4 trials**; default 21 (the source's); RSI 2 and body SMA 10 fixed.

## Ambiguities resolved

- pyramiding 0: the average-price clause only matters for adds; entries when not on that side.
- Switches default on; date window dropped. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_trend_pullback"`.

## Marks

`none`
