# #440701 Golden Bollinger Band Gap Reversion System -> `fmz_440701_rsi20_quiet_band_tick_bracket`

- FMZ source id: 440701 (lineage).
- Source: https://www.fmz.com/strategy/440701 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 11:46:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick bracket -> ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_br` [0.03, 1.0] x `adx_max` [32, 25]: **4 trials**; the same multiple for target and stop; RSI 20 and BB 60 / 2 fixed.

## Ambiguities resolved

- Tick bracket as ATR multiples. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`coarse_bar_stop`
