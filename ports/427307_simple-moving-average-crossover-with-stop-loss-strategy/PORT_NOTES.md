# #427307 Simple Moving Average Crossover with Stop Loss Strategy -> `fmz_427307_sma5_session_vwap_cross_reversal`

- FMZ source id: 427307 (lineage).
- Source: https://www.fmz.com/strategy/427307 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-19 21:42:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA against the session VWAP |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Margin_long / margin_short 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_len` [5, 10]: **2 trials**.

## Ambiguities resolved

- VWAP anchored at the broker-day start. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_cross"`.

## Marks

`none`
