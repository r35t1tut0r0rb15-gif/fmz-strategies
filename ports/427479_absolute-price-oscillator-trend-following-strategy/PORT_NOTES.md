# #427479 Absolute Price Oscillator Trend Following Strategy -> `fmz_427479_hpotter_apo`

- FMZ source id: 427479 (lineage).
- Source: https://www.fmz.com/strategy/427479 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-21 15:27:59). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C8). Not run.
- Near-duplicate group: **ND427479** (with #442834, Jaccard 0.756); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | +-3 price-unit zones -> +- `zone_atr` x ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427479. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`zone_atr` [0.02, 0.1, 0.3] x `long_ema` [20, 40]: **6 trials**; defaults 0.02 / 20; EMA 10 fixed. On 4-hour BTC bars 3 USD is about 0.01-0.02 ATR (judgement, stated before any backtest).

## Ambiguities resolved

- Zones in price units re-expressed in ATR. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`none`
