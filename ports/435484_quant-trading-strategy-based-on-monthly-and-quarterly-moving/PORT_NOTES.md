# #435484 Quant Trading Strategy Based on Monthly and Quarterly Moving Average Operation -> `fmz_435484_sma_20_60_pullback_long`

- FMZ source id: 435484 (lineage).
- Source: https://www.fmz.com/strategy/435484 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 11:49:06). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C78). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Average cross, 10-bar high pullback and a percent stop on closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [60, 50]: **4 trials**; the 10-bar high, 0.9 factors and the 10 % stop fixed.

## Ambiguities resolved

- Exits on bar closes; entry price = next open. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
