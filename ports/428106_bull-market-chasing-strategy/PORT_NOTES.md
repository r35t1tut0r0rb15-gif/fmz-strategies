# #428106 Bull Market Chasing Strategy -> `fmz_428106_ema_10_60_cross`

- FMZ source id: 428106 (lineage).
- Source: https://www.fmz.com/strategy/428106 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-28 16:23:41). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commented strategy() cash quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_fast` [10, 20] x `ema_slow` [60, 120]: **4 trials**; defaults 10 / 60 (the source's).

## Ambiguities resolved

- strategy() commented out; shorts on (default). REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
