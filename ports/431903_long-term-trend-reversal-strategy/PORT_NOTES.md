# #431903 Long Term Trend Reversal Strategy -> `fmz_431903_trend_bounce_channel`

- FMZ source id: 431903 (lineage).
- Source: https://www.fmz.com/strategy/431903 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-13 10:51:35). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C47). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at the fill |
| 2 | PASS | Donchian levels, an SMA and ATR multiples |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`nn` [7, 14] x `slm` [2.0, 3.0]: **4 trials**; SMA 200 and the 10-bar ATR fixed.

## Ambiguities resolved

- Stop fixed at the fill; close conventions as stated. REVERSAL INTENDED. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
