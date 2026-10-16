# #428093 Moving Average Direction Reversal Trading Strategy -> `fmz_428093_chartart_consecutive_bars`

- FMZ source id: 428093 (lineage).
- Source: https://www.fmz.com/strategy/428093 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-28 15:50:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Close comparisons only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`consecutive` [4, 2, 3, 5]: **4 trials**; default 4 (the source's); MA length 1 (off) fixed.

## Ambiguities resolved

- MA length 1 is "off": close vs previous close; an equal close counts as down (trend 0), as written.
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
