# #488898 Multi Factor Trend Tracking Dynamic Risk Management Stock Trading Strategy -> `fmz_488898_g_channel_ma_stack_atr_volume_rsi_exit_reversal`

- FMZ source id: 488898 (lineage).
- Source: https://www.fmz.com/strategy/488898 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-03-31 16:47:17). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket at the signal close as fractions of the fill |
| 2 | PASS | MA-stack trend states on rising volatility and volume, RSI / low-volume exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [2.0, 3.0] x `tp_atr` [4.0, 6.0]: **4 trials**; MA stacks as written, volume x 1.3 / 0.5, RSI 14 75 / 25.

## Ambiguities resolved

- Repeats re-send the bracket (pending). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_agreement"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
