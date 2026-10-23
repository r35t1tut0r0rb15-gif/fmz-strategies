# #426591 Trend Following Strategy Based on Price Volume Integration -> `fmz_426591_hma15_volume_and_close_rising_sma10_long`

- FMZ source id: 426591 (lineage).
- Source: https://www.fmz.com/strategy/426591 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-13 15:25:20). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V5). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price and volume Hull-average agreement |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty = equity / close stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hma_len` [15, 9] x `base_len` [10, 20]: **4 trials**.

## Ambiguities resolved

- Volume = broker tick volume. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_trend"`.

## Marks

`none`
