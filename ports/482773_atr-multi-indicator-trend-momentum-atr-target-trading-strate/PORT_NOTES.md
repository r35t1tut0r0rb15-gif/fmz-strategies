# #482773 多指标趋势动量ATR目标价交易策略-Multi-Indicator-Trend-Momentum-ATR-Target-Trading-Strategy -> `fmz_482773_rsi60_cross_dmi_as_named_close_atr_target_stop_long`

- FMZ source id: 482773 (lineage).
- Source: https://www.fmz.com/strategy/482773 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based ATR target / stop in the loop |
| 2 | PASS | RSI 60 crossings with DMI and RSI trend filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier_target` [2.5, 4.0] x `atr_multiplier_stop` [1.5, 3.0]: **4 trials**; DMI 14, RSI 14 / SMA 20, ATR 14.

## Ambiguities resolved

- The DMI outputs are bound in the source's (swapped) order, as written. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
