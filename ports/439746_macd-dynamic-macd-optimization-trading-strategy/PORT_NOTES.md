# #439746 经典动态MACD优化交易策略Dynamic-MACD-Optimization-Trading-Strategy -> `fmz_439746_macd16_34_10_rsi_volume_wide_stop_tight_target_reversal`

- FMZ source id: 439746 (lineage).
- Source: https://www.fmz.com/strategy/439746 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-23 14:40:38). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket at the signal close as fractions of the fill |
| 2 | PASS | MACD signal crossings with RSI and volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.105, 0.03] x `tp_pct` [0.003, 0.01]: **4 trials**; MACD 16 / 34 / 10, RSI 19, volume SMA 13.

## Ambiguities resolved

- Bracket fixed at the first signal's close; 1e-6 floor for passed levels. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`none`
