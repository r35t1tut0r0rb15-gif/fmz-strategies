# #439745 VWAP和RSI组合策略VWAP-and-RSI-Combination-Strategy -> `fmz_439745_ema50_200_vwap_rsi3_dip_close_stop_1m_long_only`

- FMZ source id: 439745 (lineage).
- Source: https://www.fmz.com/strategy/439745 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:37:22). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V23). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-based stop in the signals |
| 2 | PASS | Trend-filtered VWAP breaks after an RSI 3 dip |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_buy` [10, 20] x `stop_pct` [0.05, 0.02]: **4 trials**; EMA 50 / 200, RSI 3, sell line 90.

## Ambiguities resolved

- Session VWAP at the broker day; close-based stop from the fill price. Volume = broker tick volume (VWAP). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
