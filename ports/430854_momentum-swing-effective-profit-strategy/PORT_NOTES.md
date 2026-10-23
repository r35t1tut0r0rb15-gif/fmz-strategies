# #430854 Momentum Swing Effective Profit Strategy -> `fmz_430854_strong_bar_momentum_sma60_volume_high_ema10_exit_long`

- FMZ source id: 430854 (lineage).
- Source: https://www.fmz.com/strategy/430854 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 15:02:05). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V11). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | Strong-bar momentum above a moving average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [60, 100] x `exit_ema` [10, 20]: **4 trials**; SL 50 %, TP 30 %.

## Ambiguities resolved

- Script flag blocks re-entry after a stop / target until the EMA exit, as written. Volume = broker tick volume.
- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_breakout"`.

## Marks

`coarse_bar_stop`
