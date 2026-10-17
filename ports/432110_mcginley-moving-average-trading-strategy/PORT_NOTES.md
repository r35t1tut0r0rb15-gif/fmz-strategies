# #432110 McGinley Moving Average Trading Strategy -> `fmz_432110_mcginley_ema_pullback`

- FMZ source id: 432110 (lineage).
- Source: https://www.fmz.com/strategy/432110 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-14 15:48:46). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C49). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; target fixed at entry |
| 2 | ADAPT | Tick target -> ATR fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_atr` [0.002, 1.0] x `md_period` [20, 10]: **4 trials**; EMA 21 / 42, k 0.6 and ATR 14 fixed.

## Ambiguities resolved

- Tick target as an ATR fraction (criterion 2 ADAPT). Date window dropped. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`coarse_bar_stop`
