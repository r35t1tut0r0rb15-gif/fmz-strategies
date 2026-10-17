# #482773 多指标趋势动量ATR目标价交易策略-Multi-Indicator-Trend-Momentum-ATR-Target-Trading-Strategy -> `fmz_482773_rsi60_cross_dmi_close_atr_levels_long`

- FMZ source id: 482773 (lineage).
- Source: https://www.fmz.com/strategy/482773 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-27 17:51:29). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based exits. |
| 2 | PASS | DMI, RSI and ATR multiples. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Default quantity. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_mult` [2.5, 4.0] x `sl_mult` [1.5, 2.5]: **4 trials**; defaults 2.5 / 1.5 (the source's); DMI 14 / 14, RSI 14,
RSI SMA 20 and ATR 14 fixed.

## Ambiguities resolved

- `[adx, plusDI, minusDI] = ta.dmi(...)` unpacks (+DI, -DI, ADX) under swapped names: the filter is +DI > 18,
  -DI > ADX and +DI rising. Ported as written.
- Target and stop are tested on closes with `strategy.close`: exit signals at the next open (rule 3, #489638).
  Every signal overwrites the levels, also while held.
- Long only. Daily bars: broker days stamped with their first minute.

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_following"`.

## Marks

none
