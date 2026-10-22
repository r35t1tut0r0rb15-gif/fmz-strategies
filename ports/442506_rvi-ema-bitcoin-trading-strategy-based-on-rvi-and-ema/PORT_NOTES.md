# #442506 基于RVI和EMA的比特币交易策略Bitcoin-Trading-Strategy-Based-on-RVI-and-EMA -> `fmz_442506_rvi_cross_ema_stack_atr_levels`

- FMZ source id: 442506 (lineage).
- Source: https://www.fmz.com/strategy/442506 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-22 13:50:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C156). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RVI crossings with an EMA stack; signal-bar levels tested on the bar range |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [4, 10] x `atr_sl` [2.0, 1.0]: **4 trials**; the EMAs, the ATR length and the target multiple fixed.

## Ambiguities resolved

- Level exits read at the close, filled at the next open. Entries only from flat. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator"`.

## Marks

`none`
