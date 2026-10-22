# #475604 多层级跌幅ATH动态追踪三段买入策略-Multi-level-ATH-Dynamic-Tracking-Triple-Entry-Strategy -> `fmz_475604_ath_dip_10_15_20_recovery_5pct_long`

- FMZ source id: 475604 (lineage).
- Source: https://www.fmz.com/strategy/475604 (PineScript v6, author ChaoZhang, FMZ last
  modified 2024-12-20 14:53:04). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C228). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | All-time-high dip entries with a recovery exit |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Dollar amounts per dip stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dip1` [10.0, 20.0] x `recovery` [5.0, 2.0]: **4 trials**; dips 2 / 3 at dip1 + 5 / + 10.

## Ambiguities resolved

- The all-time high counts from the first loaded bar; pyramiding 1 (one dip unit). Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
