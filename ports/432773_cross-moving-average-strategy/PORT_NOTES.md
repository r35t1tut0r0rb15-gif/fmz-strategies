# #432773 Cross Moving Average Strategy -> `fmz_432773_vwma3_sma266_cross_delay3_fixed_bracket_reversal`

- FMZ source id: 432773 (lineage).
- Source: https://www.fmz.com/strategy/432773 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-21 13:33:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed fractional bracket from the fill |
| 2 | PASS | Delayed moving-average crossings |
| 3 | PASS | Exchange pair in the header only; tick distances converted at the source's BTC price. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow_len` [266, 200] x `delay` [3, 0]: **4 trials**; VWMA 3, TP 0.027, SL 0.0054.

## Ambiguities resolved

- Tick distances converted at about 37000 USD BTC. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
