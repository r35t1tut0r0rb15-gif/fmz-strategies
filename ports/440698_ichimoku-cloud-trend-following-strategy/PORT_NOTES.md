# #440698 Ichimoku Cloud Trend Following Strategy -> `fmz_440698_ichimoku_pullback_breakout`

- FMZ source id: 440698 (lineage).
- Source: https://www.fmz.com/strategy/440698 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-01 11:34:23). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; displaced values from past bars |
| 2 | PASS | Ichimoku lines and cloud |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital, commission and slippage settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tenkan` [9, 20] x `kijun` [26, 60]: **4 trials**; Senkou B 52 and displacement 26 fixed.

## Ambiguities resolved

- Short side uses the long breakout test, as written. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
