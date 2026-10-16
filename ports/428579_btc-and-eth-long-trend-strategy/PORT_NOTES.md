# #428579 BTC and ETH Long Trend Strategy -> `fmz_428579_btc_long_trend_filters`

- FMZ source id: 428579 (lineage).
- Source: https://www.fmz.com/strategy/428579 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-07 10:16:09). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C17). Not run.
- Near-duplicate group: **ND428579** (2 members, best partner #439200, Jaccard 0.733); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked stop. |
| 2 | PASS | MA lengths, volatility percentage, percent stop. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Position size and leverage stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND428579. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`stop_loss` [1.5, 3] x `vol_max` [2, 3]: **4 trials**; defaults 1.5 / 2 (the source's); MACD 12/26/7, EMA 20, SMA 100 / 200 fixed.

## Ambiguities resolved

- rising(x, n) as Pine; flags carried through [1]. The stop is close-checked (an exit signal), with the same-bar check after an entry as written.
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
