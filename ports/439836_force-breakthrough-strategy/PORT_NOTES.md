# #439836 Force Breakthrough Strategy -> `fmz_439836_connors_rsi2_snapback_ema10_200`

- FMZ source id: 439836 (lineage).
- Source: https://www.fmz.com/strategy/439836 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-24 11:25:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA sides and RSI 2 zone exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_os` [5, 10] x `sma_2_length` [200, 100]: **4 trials**; overbought = 100 - oversold, EMA 10 fixed.

## Ambiguities resolved

- EMAs as coded. REVERSAL INTENDED. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
