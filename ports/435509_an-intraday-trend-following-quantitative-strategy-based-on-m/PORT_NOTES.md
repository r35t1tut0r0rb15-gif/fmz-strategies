# #435509 An Intraday Trend Following Quantitative Strategy Based on Multi indicator Condition Filtering -> `fmz_435509_custom_sar_rsi50_adx_cmf_agreement_long`

- FMZ source id: 435509 (lineage).
- Source: https://www.fmz.com/strategy/435509 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-15 15:59:37). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SAR, RSI, ADX and money-flow agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 1000, commission 0.1 %, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [50, 14] x `lengthCMF` [20, 50]: **4 trials**; SAR 1.02 / 1.02 / 1.2, ADX 14, EMA 10, RSI middle 49.

## Ambiguities resolved

- SAR acceleration above 1, as written. Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
