# #427816 BBB Strategy -> `fmz_427816_bollinger_pctb_extremes`

- FMZ source id: 427816 (lineage).
- Source: https://www.fmz.com/strategy/427816 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-25 17:53:36). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C12). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | %B levels only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 50] x `mult` [2, 1.5]: **4 trials**; defaults 21 / 2 (the source's); %B lines 1.2 / 1.0 / -0.2 / 0.2 fixed.

## Ambiguities resolved

- strategy() commented out: Pine defaults. Opposite entries cannot occur (entries from flat only). FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion_band"`.

## Marks

`none`
