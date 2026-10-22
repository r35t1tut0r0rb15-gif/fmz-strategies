# #442653 Institutional Trader Strategy Based on Price Action -> `fmz_442653_fair_value_range_block_reversal`

- FMZ source id: 442653 (lineage).
- Source: https://www.fmz.com/strategy/442653 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-23 15:04:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C160). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close vs SMA with a range test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `fair_value_period` [60, 120]: **4 trials**; the 0.382 fraction fixed.

## Ambiguities resolved

- Signed difference as written. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
