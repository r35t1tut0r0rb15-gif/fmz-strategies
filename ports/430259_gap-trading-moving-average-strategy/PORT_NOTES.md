# #430259 Gap Trading Moving Average Strategy -> `fmz_430259_noro_shift_close_v10`

- FMZ source id: 430259 (lineage).
- Source: https://www.fmz.com/strategy/430259 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-26 16:05:01). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C34). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported. |
| 2 | PASS | A percentage distance from a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The lot % and pyramiding 5 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`limit` [10.0, 5.0, 2.5]: **3 trials**; SMA 3 of ohlc4 fixed.

## Ambiguities resolved

- Adds not ported. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks

`none`
