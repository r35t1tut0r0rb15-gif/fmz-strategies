# #432312 Multi Trend Strategy -> `fmz_432312_vwap_rsi_dip_linreg_rsi_peak_1m_pct_target_reversal`

- FMZ source id: 432312 (lineage).
- Source: https://www.fmz.com/strategy/432312 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-16 11:20:10). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V13). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; side-specific percent targets from the fill |
| 2 | PASS | VWAP RSI dips and regression RSI peaks with a daily cut-off |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): cash 10000 per trade, capital 10000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`long_tp` [0.003, 0.006] x `short_tp` [0.0095, 0.005]: **4 trials**; RSI 13 / 23, levels 20 / 99.8 / 95.

## Ambiguities resolved

- Session VWAP from the broker-day start; cut-off hour in UTC; later call wins on a two-sided bar.
- Targets from the fill minute (the script: from the next bar). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_threshold"`.

## Marks

`none`
