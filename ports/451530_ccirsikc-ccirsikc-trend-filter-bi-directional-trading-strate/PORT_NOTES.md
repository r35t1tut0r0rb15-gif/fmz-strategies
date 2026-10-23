# #451530 CCIRSIKC趋势滤波多空双向交易策略-CCIRSIKC-Trend-Filter-Bi-Directional-Trading-Strategy -> `fmz_451530_keltner_cci5_rsi30_flagged_entries_2h_reversal`

- FMZ source id: 451530 (lineage).
- Source: https://www.fmz.com/strategy/451530 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-15 16:56:03). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Keltner-band extremes confirmed by CCI and RSI, CCI zero-line exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): cash 50000 per order, commission 0.0005, slippage 2, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`kc_mult` [0.7, 1.5] x `cci_len` [5, 14]: **4 trials**; KC 30, RSI 30, levels 75 / 60.

## Ambiguities resolved

- Script flags as written; volume test reduces to volume > 0. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "keltner_channel"`.

## Marks

`none`
