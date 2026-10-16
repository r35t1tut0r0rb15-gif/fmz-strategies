# #430017 Fast RSI Breakthrough Strategy -> `fmz_430017_noro_fast_rsi_v12`

- FMZ source id: 430017 (lineage).
- Source: https://www.fmz.com/strategy/430017 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-24 11:51:56). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported. |
| 2 | PASS | RSI levels and body ratios. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry and pyramiding 5 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426509. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_period` [7, 14] x `limit` [30, 20]: **4 trials**; RSI bars 1, body fractions 1/4 and 1/2 fixed.

## Ambiguities resolved

- Adds (pyramiding 5) not ported; the average price is the first fill.
- Entry and exit on one bar: the bar ends flat (statement order). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
