# #188507 典型价格百分比通道-凯尔特纳与百分比通道变形 -> `fmz_188507_typical_ema_band_gate_reverse`

- Source: https://www.fmz.com/strategy/188507 (MyLanguage, author cyberking, FMZ last modified
  2020-03-05 21:36:49). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A2). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Close-price model on daily bars. |
| 2 | ADAPT | +5 % / -4.76 % percent bands -> +/- `band_atr` x ATR(14). |
| 3 | PASS | Huobi spot in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED | |

## Declared grid (criterion 5)

`n` [10, 21, 40] x `band_atr` [0.5, 1.25, 2.5] = **9 trials**.

## Ambiguities resolved

- The band gate (`DX < KRTHR`) is rarely binding: it stops entries only when the typical-price
  EMA has run far from its own EMA. Kept as written.
- The commented-out alternative entries (lines 36, 38) are not ported.
- `FREQ = "1D"` broker days from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`: close above/below an EMA, always in.

## Marks (2026-10-07)

`none`
