# #436757 Trending Darvas Box Quantitative Trading Strategy -> `fmz_436757_darvas_box_mavilimw_stop`

- FMZ source id: 436757 (lineage).
- Source: https://www.fmz.com/strategy/436757 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-27 14:45:41). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C95). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Box levels as distances from the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`boxp` [5, 8] x `rvi_len` [10, 14]: **4 trials**; MavilimW 3 / 5 fixed.

## Ambiguities resolved

- Box stop as a distance from the signal close; trade cap and date window dropped; open profit from the fill price. Entries from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

`coarse_bar_stop`
