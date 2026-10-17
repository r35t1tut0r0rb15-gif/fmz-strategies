# #430898 Oma and Apollo Dual Rail Trading Strategy -> `fmz_430898_two_ema_stoch_rsi_atr`

- FMZ source id: 430898 (lineage).
- Source: https://www.fmz.com/strategy/430898 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 17:09:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C42). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the re-based target fixed at entry (rule 2) |
| 2 | PASS | EMAs, stochastic RSI and an ATR band |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [0.7, 1.5] x `rr` [2.0, 1.0]: **4 trials**; EMA 50 / 200, stoch RSI 3 / 3 / 14 / 14, levels 20 / 80 fixed.

## Ambiguities resolved

- Pending (not emitted as written): the target re-based one bar after the entry; the signal bar's level kept.
- valuewhen reads k at the confirmation bars. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend_oscillator_pullback"`.

## Marks

`trailing_stop_pending`
