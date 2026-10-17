# #433439 基于SSL通道指标的趋势跟踪策略No-Nonsense-SSL-Channel-Trading-Strategy -> `fmz_433439_nnfx_ssl_atr_bracket`

- FMZ source id: 433439 (lineage).
- Source: https://www.fmz.com/strategy/433439 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-11-27 16:42:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C60). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar (approximation stated) |
| 2 | PASS | Channel crosses and ATR exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_mult` [1.5, 3.0] x `tp_mult` [1.0, 2.0]: **4 trials**; SSL 10 and ATR 14 (SMA) fixed.

## Ambiguities resolved

- Per-bar re-placed bracket fixed at the signal bar (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ssl_channel"`.

## Marks

`coarse_bar_stop, trailing_stop_pending`
