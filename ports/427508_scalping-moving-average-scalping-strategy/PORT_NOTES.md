# #427508 Moving Average Scalping Strategy -> `fmz_427508_ma_scalping_long`

- FMZ source id: 427508 (lineage).
- Source: https://www.fmz.com/strategy/427508 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-21 20:41:15). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C9). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Unused stop / target levels stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`signal` [9, 5, 20] x `fast` [50, 30]: **6 trials**; defaults 9 / 50 (the source's); SMA 100 / 200 fixed.

## Ambiguities resolved

- The 2 % / 8 % levels are never used by an order. Long only. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
