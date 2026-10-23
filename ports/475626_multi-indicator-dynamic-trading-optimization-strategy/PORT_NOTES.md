# #475626 Multi Indicator Dynamic Trading Optimization Strategy -> `fmz_475626_ift_combo_cci_rsi_stoch_mfi_cross_4h_reversal`

- FMZ source id: 475626 (lineage).
- Source: https://www.fmz.com/strategy/475626 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-20 16:31:21). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; position-price bracket followed in the signals |
| 2 | PASS | Inverse-Fisher oscillator combo crossings of -0.5 / 0.5 |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`level` [0.5, 0.3] x `wma_len` [9, 5]: **4 trials**; lengths 5; SL 0.5 %, TP 1 %.

## Ambiguities resolved

- Bracket from position_avg_price at the signal, followed at the next open. Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "inverse_fisher"`.

## Marks

`trailing_stop_pending`
