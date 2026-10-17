# #484773 动态ATR追踪止损交易策略市场波动性自适应系统-Dynamic-ATR-Trailing-Stop-Trading-Strategy-Market-Volatility-Adaptive-System -> `fmz_484773_atr_flip_line_cross`

- FMZ source id: 484773 (lineage).
- Source: https://www.fmz.com/strategy/484773 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-04 11:03:58). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | An ATR band. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_period` [10, 20]: **4 trials**; defaults 1 / 10 (the source's); Heikin Ashi off.

## Ambiguities resolved

- The line as written flips each bar on the close against the previous line, with no ratchet (unlike the full UT
  Bot); na while the ATR is na. The close before each entry is the reversal: REVERSAL INTENDED. Daily bars are
  broker days; FREQ = "1D".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
