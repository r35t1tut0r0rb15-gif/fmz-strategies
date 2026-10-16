# #428059 EMA Crossover Strategy -> `fmz_428059_ema_9_20_cross_4d`

- FMZ source id: 428059 (lineage).
- Source: https://www.fmz.com/strategy/428059 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-28 11:22:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | EMA lengths only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [20, 50]: **4 trials**; defaults 9 / 20 (the source's).

## Ambiguities resolved

- year > 2016 filter dropped. REVERSAL INTENDED.
- 4-day bars: blocks of broker days from 1970-01-01 (worker A's convention). FREQ = "4D".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
