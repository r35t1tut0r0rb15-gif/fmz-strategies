# #434473 Moving Average Crossover Strategy -> `fmz_434473_ema_cross_one_bar`

- FMZ source id: 434473 (lineage).
- Source: https://www.fmz.com/strategy/434473 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-06 16:58:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C67). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the as-written exits are a next-bar close |
| 2 | PASS | Average crosses |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [20, 10] x `slow` [50, 100]: **4 trials**.

## Ambiguities resolved

- Both brackets act on every position: each trade ends at the open after its fill bar, as written (the per-side bracket owed). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
