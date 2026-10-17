# #435232 Volatility Breakthrough Strategy -> `fmz_435232_vtm_four_condition_state`

- FMZ source id: 435232 (lineage).
- Source: https://www.fmz.com/strategy/435232 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-13 14:36:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Averages, MACD and ADX states |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [48, 100] x `adx_th` [25, 20]: **4 trials**; MACD 12 / 26 / 9, BB 20 and ADX 14 fixed.

## Ambiguities resolved

- Unarmed exits dropped. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
