# #483126 基于RSI和随机RSI的双重动量趋势反转策略-Dual-Momentum-Trend-Reversal-Strategy-Based-on-RSI-and-Stochastic-RSI -> `fmz_483126_rsi_stochrsi_cross_reversal`

- FMZ source id: 483126 (lineage).
- Source: https://www.fmz.com/strategy/483126 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 16:53:04). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L19). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI and stochastic RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stoch_os` [20, 30] x `stoch_ob` [80, 70]: **4 trials**; defaults 20 / 80 (the source's); RSI 14 (70 / 30) and the
stochastic RSI 14 / 3 / 3 fixed.

## Ambiguities resolved

- A short signal while long also meets the long exit: close + entry is a reversal, so only the entry is emitted
  (long side mirrored).
- REVERSAL INTENDED. No stops. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "oscillator_cross"`.

## Marks

`none`
