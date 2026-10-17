# #430874 动态RSI震荡操作策略Dynamic-RSI-Oscillation-Trading-Strategy -> `fmz_430874_weekly_level_rsi_dips_long`

- FMZ source id: 430874 (lineage).
- Source: https://www.fmz.com/strategy/430874 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-02 16:04:07). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; adds not ported |
| 2 | PASS | A weekly level and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the capital % lot formula stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [7, 14] x `rsi_limit` [30, 20]: **4 trials**; the weekly ohlc4 level and both filters fixed on.

## Ambiguities resolved

- Weekly level from the last completed broker week. Adds not ported. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
