# #439624 动态移动EMAS组合量化策略Dynamic-Moving-EMAs-Combination-Quant-Strategy -> `fmz_439624_ema_ladder_breakout_crypto_max`

- FMZ source id: 439624 (lineage).
- Source: https://www.fmz.com/strategy/439624 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-22 12:34:33). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C122). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA ladder and high / low runs |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [3, 5] x `length4` [50, 34]: **4 trials**; the other ladder lengths fixed.

## Ambiguities resolved

- Closes after entries. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
