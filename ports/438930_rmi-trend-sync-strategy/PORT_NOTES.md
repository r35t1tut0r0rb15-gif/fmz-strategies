# #438930 RMI Trend Sync Strategy -> `fmz_438930_rsi_mfi_momentum_cross_ema5_slope_3h_reversal`

- FMZ source id: 438930 (lineage).
- Source: https://www.fmz.com/strategy/438930 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-16 14:10:25). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V22). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI / MFI momentum crossings with an EMA slope |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [21, 14] x `pmom` [70, 65]: **4 trials**; nmom 30, EMA 5.

## Ambiguities resolved

- na momentum treated as false; the supertrend exits never act. Volume = broker tick volume (MFI). REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mfi_threshold"`.

## Marks

`none`
