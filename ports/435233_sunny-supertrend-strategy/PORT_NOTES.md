# #435233 Sunny Supertrend Strategy -> `fmz_435233_sunny_supertrend_flips`

- FMZ source id: 435233 (lineage).
- Source: https://www.fmz.com/strategy/435233 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 14:40:24). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C75). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`factor` [3.0, 2.0] x `atr_len` [10, 20]: **4 trials**.

## Ambiguities resolved

- Exits on non-existent ids: none, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
