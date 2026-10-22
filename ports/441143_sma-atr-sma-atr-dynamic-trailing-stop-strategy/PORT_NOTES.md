# #441143 基于SMA和ATR的跟踪止损策略SMA-ATR-Dynamic-Trailing-Stop-Strategy -> `fmz_441143_sma200_atr_band_trend_long`

- FMZ source id: 441143 (lineage).
- Source: https://www.fmz.com/strategy/441143 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-06 10:06:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C147). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA and ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sma_length` [200, 100] x `atr_length` [14, 28]: **4 trials**.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
