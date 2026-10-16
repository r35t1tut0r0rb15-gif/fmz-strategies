# #428086 Moving Average Support and Resistance Breakout Strategy -> `fmz_428086_lunaowl_sr_breakout`

- FMZ source id: 428086 (lineage).
- Source: https://www.fmz.com/strategy/428086 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 15:20:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Equity quantity, slippage, commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lb` [50, 20, 100, 30]: **4 trials**; default 50 (the source's).

## Ambiguities resolved

- cross() is either direction: R and S come from the same events; occurrence 1 = the cross before the latest (valuewhen).
- REVERSAL INTENDED. Broker-day bars; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_breakout"`.

## Marks

`none`
