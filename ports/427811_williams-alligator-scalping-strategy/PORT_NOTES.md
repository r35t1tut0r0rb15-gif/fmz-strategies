# #427811 Williams Alligator Scalping Strategy -> `fmz_427811_alligator_heikin_ashi`

- FMZ source id: 427811 (lineage).
- Source: https://www.fmz.com/strategy/427811 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-25 17:42:27). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Heikin Ashi of the chart's own bars; bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the off bracket stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`jaw` [13, 21] x `ma_type` [1 SMA, 2 EMA]: **4 trials**; defaults 13 / SMA (the source's); teeth 8 and lips 5 fixed.

## Ambiguities resolved

- WMA, linreg and VWMA options not ported (VWMA uses volume). Plot offsets do not reach the conditions.
- Bracket / trail inputs default to 0 (off). REVERSAL INTENDED.
- 4-day bars: blocks of broker days from 1970-01-01 (worker A's convention). FREQ = "4D". The source's note says it was meant for 1-5 minute charts; the header's 4d is ported.

## FAMILY (proposed, user to confirm)

`FAMILY = "alligator"`.

## Marks

`none`
