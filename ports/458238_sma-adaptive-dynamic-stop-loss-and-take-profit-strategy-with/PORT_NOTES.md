# #458238 SMA交叉与成交量过滤的自适应动态止盈止损策略Adaptive-Dynamic-Stop-Loss-and-Take-Profit-Strategy-with-SMA-Crossover-and-Volume-Filter -> `fmz_458238_sma7_25_cross_volume_1_2pct_bracket_50bar_1h_reversal`

- FMZ source id: 458238 (lineage).
- Source: https://www.fmz.com/strategy/458238 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-07-31 11:20:39). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V32). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket at the signal close as fractions of the fill; 50-bar time exit |
| 2 | PASS | SMA 7 / 25 crossings with volume filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl` [0.01, 0.015] x `tp` [0.02, 0.03]: **4 trials**; SMA 7 / 25, volume SMA 20, 50 bars.

## Ambiguities resolved

- Bracket at the signal close; short needs low volume (as written). Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
