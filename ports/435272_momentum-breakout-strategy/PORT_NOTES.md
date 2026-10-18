# #435272 Momentum Breakout Strategy -> `fmz_435272_three_ma_laguerre_adx`

- FMZ source id: 435272 (lineage).
- Source: https://www.fmz.com/strategy/435272 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-13 17:08:53). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C77). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | REVIEW | Tick bracket switch off by default: not ported |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the tick bracket inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema1_len` [16, 8] x `adx_th` [20, 25]: **4 trials**; EMA 48, SMA 200, alpha 0.2 and ADX 14 fixed.

## Ambiguities resolved

- Tick bracket (off by default) not ported. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
