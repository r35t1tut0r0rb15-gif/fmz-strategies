# #430744 双向ATR波浪交易策略Dual-ATR-Channel-Trend-Following-Strategy -> `fmz_430744_nononsense_forex_aroon`

- FMZ source id: 430744 (lineage).
- Source: https://www.fmz.com/strategy/430744 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-01 11:40:07). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C38). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | ADAPT | Price-unit stop / target -> ATR fractions. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out order size stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.008, 1.0] x `tp_atr` [0.0001, 1.0]: **4 trials**; the baseline, Aroon and confirmation settings fixed.

## Ambiguities resolved

- Price-unit SL / TP -> ATR fractions (the source's target is near zero). REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
