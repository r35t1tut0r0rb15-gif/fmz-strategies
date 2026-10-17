# #431693 双均线RSI指标组合反转策略Dual-Moving-Average-RSI-Indicator-Combination-Reversal-Strategy -> `fmz_431693_senpai_quiet_band_fade`

- FMZ source id: 431693 (lineage).
- Source: https://www.fmz.com/strategy/431693 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-10 18:01:09). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C46). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; a three-bar exit |
| 2 | PASS | ADX, Bollinger bands, RSI and PSAR |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 10 per entry stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_max` [18.5, 25.0] x `hold` [3, 6]: **4 trials**; ADX 30 / 30, BB 50 / 0.5, RSI 14 and PSAR fixed.

## Ambiguities resolved

- RSI quirk as written; close conventions as stated. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
