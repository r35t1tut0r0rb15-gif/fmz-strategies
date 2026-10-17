# #433562 基于RSI和ATR通道的超级scalping策略 -> `fmz_433562_big_candle_rsi_momentum`

- FMZ source id: 433562 (lineage).
- Source: https://www.fmz.com/strategy/433562 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-28 15:15:14). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle body against the ATR and an RSI level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fixed quantity 1 stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_mult` [1.0, 1.5] x `atr_len` [14, 28]: **4 trials**; RSI 14 / 50 fixed.

## Ambiguities resolved

- Unused stop / target variables dropped. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`none`
