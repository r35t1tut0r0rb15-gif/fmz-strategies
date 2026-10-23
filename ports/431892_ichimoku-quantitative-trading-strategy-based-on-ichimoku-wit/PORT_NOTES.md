# #431892 基于Ichimoku的多信号量化交易策略Quantitative-Trading-Strategy-Based-on-Ichimoku-with-Multiple-Signals -> `fmz_431892_ichimoku_price_vs_kumo_state_reversal`

- FMZ source id: 431892 (lineage).
- Source: https://www.fmz.com/strategy/431892 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 10:24:35). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price against the Ichimoku cloud |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kijun_len` [26, 30] x `senkou_b_len` [52, 60]: **4 trials**; Tenkan 9, shift 26.

## Ambiguities resolved

- Default signal only; no close is ever sent (the opposite entry ends a position). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
