# #440863 Dual Breakthrough Moving Average Trading Strategy -> `fmz_440863_sar_sma_macd_rsi_agreement_long`

- FMZ source id: 440863 (lineage).
- Source: https://www.fmz.com/strategy/440863 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:33:14). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR, SMA, MACD and RSI agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`malen` [200, 100] x `rsilen` [7, 14]: **4 trials**; SAR and MACD fixed.

## Ambiguities resolved

- Long only (shorts off by default). FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
