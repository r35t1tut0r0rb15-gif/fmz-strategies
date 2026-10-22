# #468325 EMA与CCI多重交叉趋势追踪策略-Multi-EMA-and-CCI-Crossover-Trend-Following-Strategy -> `fmz_468325_ema8_12_24_cross_ema72_cci150_two_bracket_kinds_from_flat`

- FMZ source id: 468325 (lineage).
- Source: https://www.fmz.com/strategy/468325 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-09-26 15:43:50). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C207). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the entry-price brackets as fixed fractions |
| 2 | PASS | Clustered EMA crossings with CCI confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Percent-of-equity size stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`max_wait` [2, 4] x `cci_level` [150, 100]: **4 trials**; the EMA lengths and the four bracket sizes fixed.

## Ambiguities resolved

- Bracket kind from the signal bar's test (Long_one first). Entries only from flat. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`coarse_bar_stop`
