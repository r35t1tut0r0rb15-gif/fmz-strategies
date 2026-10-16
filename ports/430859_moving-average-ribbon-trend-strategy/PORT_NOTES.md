# #430859 Moving Average Ribbon Trend Strategy -> `fmz_430859_noro_trend_ribbon`

- FMZ source id: 430859 (lineage).
- Source: https://www.fmz.com/strategy/430859 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 15:22:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A channel of a moving average. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks

`none`
