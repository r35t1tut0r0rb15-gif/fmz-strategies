# #477961 Triple Bottom Rebound Momentum Breakthrough Strategy -> `fmz_477961_ema5_20_cross_atr2_bracket_reversal`

- FMZ source id: 477961 (lineage).
- Source: https://www.fmz.com/strategy/477961 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-01-10 15:49:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C237). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; signal-bar ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with an ATR bracket (the breakout branch never fires) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Capital stored; costs not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_factor` [2.0, 1.0] x `profit_factor` [2.0, 4.0]: **4 trials**; EMA 5 / 20, ATR 14.

## Ambiguities resolved

- The three-bounce breakout never fires, as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`coarse_bar_stop`
