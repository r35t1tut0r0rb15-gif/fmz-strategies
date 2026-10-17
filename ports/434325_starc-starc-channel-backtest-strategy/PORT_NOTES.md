# #434325 STARC通道回测策略STARC-Channel-Backtest-Strategy -> `fmz_434325_starc_band_side`

- FMZ source id: 434325 (lineage).
- Source: https://www.fmz.com/strategy/434325 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-05 14:52:20). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C66). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_len` [5, 10] x `k` [1.33, 2.0]: **4 trials**; ATR 15 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
