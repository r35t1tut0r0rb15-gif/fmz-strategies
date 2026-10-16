# #427886 Level-by-Level Build-Up Moving Average Strategy -> `fmz_427886_atr_renko_second_brick_long`

- FMZ source id: 427886 (lineage).
- Source: https://www.fmz.com/strategy/427886 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 16:00:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 50 % of equity, pyramiding 2 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_length` [14, 7, 28, 50]: **4 trials**; default 14 (the source's).

## Ambiguities resolved

- TimeFrame "D" equals the daily chart: security is the series itself.
- pyramiding 2 is sizing; the entry fires once per up run. Long only. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "renko_bricks"`.

## Marks

`none`
