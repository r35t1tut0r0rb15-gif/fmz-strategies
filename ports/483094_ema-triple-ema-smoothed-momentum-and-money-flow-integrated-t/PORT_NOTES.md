# #483094 三重EMA平滑动量与资金流量综合交易策略-Triple-EMA-Smoothed-Momentum-and-Money-Flow-Integrated-Trading-Strategy -> `fmz_483094_triple_ema_roc_mfi_state_2d_reversal`

- FMZ source id: 483094 (lineage).
- Source: https://www.fmz.com/strategy/483094 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:25:57). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed momentum side confirmed by money flow |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [7, 14] x `smooth` [3, 5]: **4 trials**; MFI 14, 50 / 80 / 20.

## Ambiguities resolved

- Entries are states. Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "2D".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum"`.

## Marks

`none`
