# #427923 EMA Close Strategy -> `fmz_427923_ema_stack_vs_ema55`

- FMZ source id: 427923 (lineage).
- Source: https://www.fmz.com/strategy/427923 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-26 20:09:08). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len4` [55, 100] x `len3` [21, 34]: **4 trials**; defaults 55 / 21 (the source's); EMAs 8 / 13 fixed.

## Ambiguities resolved

- EMA 200 drawn only. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
