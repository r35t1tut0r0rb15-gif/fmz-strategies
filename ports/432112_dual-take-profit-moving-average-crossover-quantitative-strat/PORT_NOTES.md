# #432112 Dual Take Profit Moving Average Crossover Quantitative Strategy -> `fmz_432112_ema_wma_cross_tick_bracket`

- FMZ source id: 432112 (lineage).
- Source: https://www.fmz.com/strategy/432112 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 16:04:33). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick distances -> ATR fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Size 1, the risk input and the half-size first target stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.13, 1.0] x `tp_atr` [0.27, 2.0]: **4 trials**; EMA 10 / WMA 20 and ATR 14 fixed.

## Ambiguities resolved

- The half-size first target is sizing; the full position takes the second target. Tick bracket as ATR fractions. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
