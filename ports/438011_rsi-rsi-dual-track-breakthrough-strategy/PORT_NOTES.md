# #438011 基于RSI指标的双轨突破策略RSI-Dual-track-Breakthrough-Strategy -> `fmz_438011_rsi14_10_atr_close_trail_long`

- FMZ source id: 438011 (lineage).
- Source: https://www.fmz.com/strategy/438011 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-08 10:28:26). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C107). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-tested exits |
| 2 | PASS | RSI levels and ATR distances |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multi` [2.0, 3.0] x `rsi_low` [40, 30]: **4 trials**; ATR 26, RSI exit 70 and ratio 3 fixed.

## Ambiguities resolved

- Close-tested trail from the signal bar's ATR buffer; RSI exit measured from the signal close. Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
