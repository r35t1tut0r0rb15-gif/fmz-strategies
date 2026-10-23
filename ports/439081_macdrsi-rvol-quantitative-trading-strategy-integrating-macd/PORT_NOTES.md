# #439081 融合MACDRSI和RVOL的量化交易策略Quantitative-Trading-Strategy-Integrating-MACD-RSI-and-RVOL -> `fmz_439081_rsi_macd_rvol_two_of_three_crossings_reversal`

- FMZ source id: 439081 (lineage).
- Source: https://www.fmz.com/strategy/439081 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-17 15:50:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Two-of-three RSI / MACD / relative-volume crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rvol_up` [2.0, 1.5] x `rsi_len` [14, 9]: **4 trials**; RSI 30 / 70, MACD 12 / 26 / 9, RVOL down 5.

## Ambiguities resolved

- Later call wins on a two-sided bar. Volume = broker tick volume (RVOL). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
