# #440797 Parabolic Period and Bollinger Band Combined Moving Stop Loss Strategy -> `fmz_440797_heikin_ashi_sar_flip_swing_stop`

- FMZ source id: 440797 (lineage).
- Source: https://www.fmz.com/strategy/440797 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-02 11:05:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C139). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry from signal-bar data |
| 2 | PASS | Heikin-Ashi close, SAR, EMA and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Quantity, capital and slippage settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`swing` [10, 20] x `ema_v` [200, 100]: **4 trials**; RSI 14 and SAR settings fixed.

## Ambiguities resolved

- Swing-distance stop from the signal bar; SAR closes bar-tested. Entries only from flat. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "parabolic_sar"`.

## Marks

`coarse_bar_stop`
