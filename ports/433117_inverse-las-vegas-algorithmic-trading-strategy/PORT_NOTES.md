# #433117 Inverse Las Vegas Algorithmic Trading Strategy -> `fmz_433117_inverted_daily_close_compare`

- FMZ source id: 433117 (lineage).
- Source: https://www.fmz.com/strategy/433117 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 15:19:03). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C58). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed broker days |
| 2 | PASS | A close against an earlier close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital bookkeeping stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lag_days` [1, 0]: **2 trials** (1 = close[1] of the last completed day as written; 0 = the last completed close).

## Ambiguities resolved

- Reference = close[1] of the last completed broker day. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
