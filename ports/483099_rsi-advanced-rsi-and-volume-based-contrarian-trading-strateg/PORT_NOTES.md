# #483099 量化交易中基于RSI与成交量的高级反转策略-Advanced-RSI-and-Volume-Based-Contrarian-Trading-Strategy -> `fmz_483099_rsi_extreme_volume_midline_exit_reversal`

- FMZ source id: 483099 (lineage).
- Source: https://www.fmz.com/strategy/483099 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 13:31:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI extremes on volume with midline exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`os` [30.0, 25.0] x `vol_len` [20, 50]: **4 trials**; RSI 14, OB = 100 - OS.

## Ambiguities resolved

- Entries are states. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_reversion"`.

## Marks

`none`
