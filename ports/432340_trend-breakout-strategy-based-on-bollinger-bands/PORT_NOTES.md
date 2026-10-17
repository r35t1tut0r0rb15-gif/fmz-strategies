# #432340 Trend Breakout Strategy Based on Bollinger Bands -> `fmz_432340_noro_band_scalper`

- FMZ source id: 432340 (lineage).
- Source: https://www.fmz.com/strategy/432340 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-11-16 16:24:12). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C51). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Close channel, candle colours and body sizes against their own average |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the qty-0 entries stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG432340, ND426995. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10, 40]: **3 trials**; the body SMA 100 and take 0 % fixed.

## Ambiguities resolved

- Qty-0 entries only close. Avg price = the fill price. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
