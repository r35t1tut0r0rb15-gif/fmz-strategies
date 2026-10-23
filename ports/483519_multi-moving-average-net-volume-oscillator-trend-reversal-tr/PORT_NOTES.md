# #483519 Multi Moving Average Net Volume Oscillator Trend Reversal Trading Strategy -> `fmz_483519_net_volume_oscillator_wma21_ema9_state_1_2pct_reversal`

- FMZ source id: 483519 (lineage).
- Source: https://www.fmz.com/strategy/483519 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:46:30). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; 1 % / 2 % bracket from the fill |
| 2 | PASS | Smoothed close-location oscillator against its EMA |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [21, 14] x `sl` [0.01, 0.02]: **4 trials**; EMA 9 overlay, TP 2 %.

## Ambiguities resolved

- Volume cancels out. Bracket from the fill (source: from the bar after). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volume_oscillator"`.

## Marks

`coarse_bar_stop`
