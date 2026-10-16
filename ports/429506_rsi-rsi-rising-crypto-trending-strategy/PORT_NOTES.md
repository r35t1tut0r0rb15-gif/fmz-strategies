# #429506 RSI上升的加密趋势策略RSI-Rising-Crypto-Trending-Strategy -> `fmz_429506_rsi_rising_not_sideways`

- FMZ source id: 429506 (lineage).
- Source: https://www.fmz.com/strategy/429506 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-17 17:08:31). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI, %B and percentage tests only. |
| 3 | PASS | "Crypto" in the name only; exchange pair in the header. |
| 4 | DONE | The strategy() 100 % of equity and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [19, 10] x `smooth` [14, 7]: **4 trials**; the %B and ROC filters fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
