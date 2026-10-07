# #364535 2 Moving Average Color Direction Detection -> `fmz_364535_sma_8_20_cross`

- Source: https://www.fmz.com/strategy/364535 (PineScript v3, author ChaoZhang, FMZ last
  modified 2022-05-20 16:44:13). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slow` [20, 30, 50] x `fast` [5, 8, 13] = **9 trials**.

## Ambiguities resolved

- Both MA types default SMA; the direction colours only draw.
- `crossunder(ma1, ma2)` (slow under fast) is the long signal, as coded.
- No bar size in the source: `FREQ = "bar_size_pending"` (rule 1).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`bar_size_pending`
