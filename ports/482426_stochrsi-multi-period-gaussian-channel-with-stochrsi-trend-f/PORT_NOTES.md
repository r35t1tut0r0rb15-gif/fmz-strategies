# #482426 多周期高斯通道结合StochRSI趋势跟踪策略-Multi-Period-Gaussian-Channel-with-StochRSI-Trend-Following-Strategy -> `fmz_482426_ehlers_gaussian_channel_break_stoch_rsi_long`

- FMZ source id: 482426 (lineage).
- Source: https://www.fmz.com/strategy/482426 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 13:50:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L36). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A recursive price filter, a filtered true range and a stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity; the commission is a cost. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [144, 72] x `multiplier` [1.414, 2.0]: **4 trials**; defaults 144 / 1.414 (the source's); 4 poles and the
stochastic RSI 14 / 14 / 3 fixed.

## Ambiguities resolved

- `f_filt9x` is the binomial pole recursion with `nz()` (0 before the first bar); its coefficients are written out
  as C(n, k) with alternating signs. Reduced-lag / fast-response are off; the date inputs are unused.
- Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "breakout"`.

## Marks

none
