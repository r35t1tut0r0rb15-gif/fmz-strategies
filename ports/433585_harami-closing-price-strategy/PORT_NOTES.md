# #433585 Harami Closing Price Strategy -> `fmz_433585_noro_harami_long`

- FMZ source id: 433585 (lineage).
- Source: https://www.fmz.com/strategy/433585 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-28 16:50:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C62). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle shapes and body ratios |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_len` [10, 20] x `exit_frac` [0.5, 1.0]: **4 trials**.

## Ambiguities resolved

- Shorts off (quantity 0): the bearish harami only closes. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
