# #486572 高级EMA交叉动量趋势捕捉策略-Advanced-EMA-Crossover-Momentum-Trend-Capture-Strategy -> `fmz_486572_ema13_cross_adx_volume_atr_target_no_stop_2h`

- FMZ source id: 486572 (lineage).
- Source: https://www.fmz.com/strategy/486572 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-03-14 09:48:47). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; high / low-checked target in the signals |
| 2 | PASS | EMA crossings on strong-trend volume spikes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Commission stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [13, 21] x `tp_atr` [1.5, 2.5]: **4 trials**; DMI 14, ADX 30, volume SMA 5 x 1.5, ATR 14.

## Ambiguities resolved

- No stop; target checked on the bar's high / low. Volume = broker tick volume. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
