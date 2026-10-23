# #427527 Trend Following Strategy Based on Volume weighted Average Price and Volatility -> `fmz_427527_vwap_ichimoku_lead_lines_bb_tsv_long`

- FMZ source id: 427527 (lineage).
- Source: https://www.fmz.com/strategy/427527 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 21:32:40). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V7). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | VWAP lead lines with a volume-flow and band breakout filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity, capital 1000, commission 0.025 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_length` [20, 10] x `tsv_length` [13, 26]: **4 trials**; VWAP lines 9 / 26 / 5 / 13.

## Ambiguities resolved

- Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_weighted_ma"`.

## Marks

`none`
