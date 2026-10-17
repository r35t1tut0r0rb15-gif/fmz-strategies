# #433128 RSI跳空反转策略RSI-Gap-Reversal-Strategy -> `fmz_433128_rsi8_extremes_tick_bracket`

- FMZ source id: 433128 (lineage).
- Source: https://www.fmz.com/strategy/433128 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-24 16:01:31). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; bar-count exits as signals |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the tick brackets quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_per_100_ticks` [0.01, 0.1] x `length` [8, 14]: **4 trials**; the RSI levels, bar counts and tick numbers fixed.

## Ambiguities resolved

- Tick brackets as ATR (BTC and GBP readings in the grid), side taken from the signal. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
