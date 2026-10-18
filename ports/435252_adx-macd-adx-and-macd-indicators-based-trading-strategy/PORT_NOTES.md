# #435252 基于ADX和MACD指标的交易策略ADX-and-MACD-Indicators-based-Trading-Strategy -> `fmz_435252_adx_macd_agreement`

- FMZ source id: 435252 (lineage).
- Source: https://www.fmz.com/strategy/435252 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 15:45:24). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C76). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Exits on a missing id: as written, none |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The stop loss input 100 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND368715. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`di_len` [14, 21] x `macd_fast` [12, 8]: **4 trials**; MACD 26 / 9 fixed.

## Ambiguities resolved

- Exits on a missing id: none, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
