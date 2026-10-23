# #488894 Quantitative Multi Factor Dynamic Options Trading Strategy -> `fmz_488894_bollinger_breakout_volume_vwma_atr_close_exits_3bar_1h_reversal`

- FMZ source id: 488894 (lineage).
- Source: https://www.fmz.com/strategy/488894 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-31 16:38:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V45). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked ATR target / stop and a 3-bar time exit in the signals |
| 2 | PASS | Bollinger breakouts on volume with RSI, VWMA and volatility filters |
| 3 | PASS | Exchange pair in the header only (Bank Nifty named in the alerts). |
| 4 | DONE | 2 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`hold` [3, 6] x `tp_atr` [2.0, 3.0]: **4 trials**; BB 20 x 2, RSI 14, volume SMA 10 x 1.5, VWMA 20, stop 1.5 ATR.

## Ambiguities resolved

- Close-checked exits with the current ATR. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
