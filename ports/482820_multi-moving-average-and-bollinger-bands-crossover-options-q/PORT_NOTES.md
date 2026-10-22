# #482820 Multi Moving Average and Bollinger Bands Crossover Options Quantitative Trading Strategy -> `fmz_482820_sma5_11_cross_bb22_1_5_beyond_sma55_side_reversal`

- FMZ source id: 482820 (lineage).
- Source: https://www.fmz.com/strategy/482820 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 14:53:43). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C250). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-sent ATR bracket pending |
| 2 | PASS | SMA crossings beyond the Bollinger bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 3] x `dev` [1.5, 2.0]: **4 trials**; SMA 11 / 55, band length 22.

## Ambiguities resolved

- The bracket re-sent each bar from the close is pending, not ported. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`trailing_stop_pending`
