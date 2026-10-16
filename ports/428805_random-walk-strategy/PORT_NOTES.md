# #428805 Random Walk Strategy -> `fmz_428805_random_entry_bracket`

- FMZ source id: 428805 (lineage).
- Source: https://www.fmz.com/strategy/428805 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 16:10:24). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Percentages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`seed` [200, 777] x `stop_loss` [30, 60] (x 0.1 %): **4 trials**; take profit 30 (x 0.1 %) fixed.

## Ambiguities resolved

- Bracket re-based on the fill price; flat tracked through the bracket on bars. Entries from flat only.
- Mark coarse_bar_stop. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "stop_and_reverse_bracket"`.

## Marks

`coarse_bar_stop`
