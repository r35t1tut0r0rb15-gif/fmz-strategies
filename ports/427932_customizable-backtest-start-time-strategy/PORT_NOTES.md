# #427932 Customizable Backtest Start Time Strategy -> `fmz_427932_sma_14_28_cross_2d`

- FMZ source id: 427932 (lineage).
- Source: https://www.fmz.com/strategy/427932 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-09-26 20:53:15). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [14, 10] x `slow` [28, 50]: **4 trials**; defaults 14 / 28 (the source's).

## Ambiguities resolved

- Start-time filter dropped (backtest window). REVERSAL INTENDED.
- 2-day bars: blocks of broker days from 1970-01-01 (worker A's convention). FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
