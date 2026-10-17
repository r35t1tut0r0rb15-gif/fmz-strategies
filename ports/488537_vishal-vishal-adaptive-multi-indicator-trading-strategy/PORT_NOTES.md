# #488537 Vishal-自适应多指标交易策略-Vishal-Adaptive-Multi-Indicator-Trading-Strategy -> `fmz_488537_macd_sar_supertrend_agreement`

- FMZ source id: 488537 (lineage).
- Source: https://www.fmz.com/strategy/488537 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-28 17:17:56). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD, SAR and SuperTrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The equity percentage quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`st_factor` [3.0, 2.0] x `sar_max` [0.2, 0.1]: **4 trials**; defaults 3 / 0.2 (the source's); MACD 13 / 27 / 9,
SuperTrend ATR 11 and SAR step 0.02 fixed.

## Ambiguities resolved

- The three flags keep their last state, as written; the SAR exits are close-based (exits on a reversal bar are left
  to the reversal). REVERSAL INTENDED.
- Two-day bars from broker days in fixed blocks from 1970-01-01 (decision owed), as #426509.

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
