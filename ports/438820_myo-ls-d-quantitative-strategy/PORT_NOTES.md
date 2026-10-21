# #438820 Myo_LS_D Quantitative Strategy -> `fmz_438820_myo_point_count_daily_baseline`

- FMZ source id: 438820 (lineage).
- Source: https://www.fmz.com/strategy/438820 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-15 14:56:03). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C113). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; daily values from completed days |
| 2 | ADAPT | Price-unit "> 3" tests -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / close quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trend_l` [400, 200] x `base_periods` [8, 20]: **4 trials**; the other lengths fixed; rrr_frac 1e-4.

## Ambiguities resolved

- Never-scored points as written; price-unit "> 3" as fractions; short wins a both-setup flat bar. Entries only from flat. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
