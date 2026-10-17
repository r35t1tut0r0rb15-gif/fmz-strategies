# #489149 多周期波动跟踪量化策略-Multi-Timeframe-Volatility-Tracking-Quantitative-Strategy -> `fmz_489149_ema_3_8_cross_spaced_atr_bracket_long`

- FMZ source id: 489149 (lineage).
- Source: https://www.fmz.com/strategy/489149 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-04-02 10:50:32). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at the signal bar. |
| 2 | PASS | EMAs and ATR multiples. |
| 3 | PASS | "DOGE/USDT" in the title and the exchange pair only. |
| 4 | DONE | 5x leverage and the 1 %-risk quantity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trade_interval` [72, 30] x `tp_mult` [2.0, 3.0]: **4 trials**; defaults 72 / 2 (the source's); EMA 3 / 8 / 55,
ATR 14 and SL 1.2 ATR fixed.

## Ambiguities resolved

- Entries only from flat: simulate() follows the house bracket on bars; the spacing counts from the last signal bar.
- Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
