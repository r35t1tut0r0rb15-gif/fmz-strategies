# #435774 RSI通道价差跟踪策略RSI-Channel-Price-Difference-Tracking-Strategy -> `fmz_435774_hull_rsi_band_fade`

- FMZ source id: 435774 (lineage).
- Source: https://www.fmz.com/strategy/435774 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-18 17:48:24). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C81). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed RSI bands |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [13, 21] x `hma_len` [3, 5]: **4 trials**; levels 70 / 30 and the 55 / 45 channel fixed.

## Ambiguities resolved

- Status machine inside the script; hma lengths cut to whole bars. Opposite entries cannot occur. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
