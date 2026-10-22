# #443133 Multiple Moving Average Trading Strategy -> `fmz_443133_macd_cross_sma_gap_unit_bracket`

- FMZ source id: 443133 (lineage).
- Source: https://www.fmz.com/strategy/443133 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 14:32:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit gap and bracket -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bracket_frac` [1.43e-06, 0.01] x `gap_frac` [7.1e-07, 0.005]: **4 trials**; the MACD and SMA lengths fixed.

## Ambiguities resolved

- Price-unit gap and bracket as fractions of the close. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`coarse_bar_stop`
