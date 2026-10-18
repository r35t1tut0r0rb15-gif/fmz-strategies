# #435772 动量TD反转交易策略Momentum-TD-Reversal-Trading-Strategy -> `fmz_435772_sequential_count_entries_trail`

- FMZ source id: 435772 (lineage).
- Source: https://www.fmz.com/strategy/435772 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 17:40:10). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; trailing stop native |
| 2 | ADAPT | Price-unit trail -> percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The trailing-stop inputs quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bars_count` [9, 8] x `trail_pct` [0.00025, 0.002]: **4 trials**; lag 4 fixed.

## Ambiguities resolved

- barssince counts; price-unit trail -> percent trail (mark trailing_stop). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "sequential_count"`.

## Marks

`trailing_stop`
