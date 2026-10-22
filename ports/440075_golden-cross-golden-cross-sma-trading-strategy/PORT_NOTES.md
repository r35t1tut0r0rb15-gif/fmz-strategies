# #440075 双均线交叉-golden-cross-交易策略Golden-Cross-SMA-Trading-Strategy -> `fmz_440075_kiss_sma13_30_weekly_trend_bracket`

- FMZ source id: 440075 (lineage).
- Source: https://www.fmz.com/strategy/440075 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-26 14:29:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; weekly values from completed weeks; percent bracket from the fill |
| 2 | ADAPT | Price-unit slope gap -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sh_len` [13, 20] x `lg_len` [30, 50]: **4 trials**; stop 12 %, target 25 % and WiT 1 fixed.

## Ambiguities resolved

- Weekly close from the last completed broker week; slope gap as a fraction. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
