# #438470 Multi level Moving Average Crossing Strategy for Quant Masters -> `fmz_438470_sma50_100_entry_sma9_50_exit_long`

- FMZ source id: 438470 (lineage).
- Source: https://www.fmz.com/strategy/438470 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-12 12:11:02). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C110). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Moving-average crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size, capital and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429460. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`inlong` [100, 200] x `inshort` [9, 20]: **4 trials**; SMA 50 fixed.

## Ambiguities resolved

- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
