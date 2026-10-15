# #427142 Moving Average Bollinger Band Fusion Trading Strategy -> `fmz_427142_ma_zorrillo`

- FMZ source id: 427142 (lineage).
- Source: https://www.fmz.com/strategy/427142 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-18 16:08:43). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C2). Not run.
- Near-duplicate group: **DG427142** (with #434978, Jaccard 0.952); ported anyway (rule 7).

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | MA lengths, band in standard deviations. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG427142. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ma_long` [89, 55] x `bb_length` [24, 20] x `lookback` [64, 32]: **8 trials**; defaults 89 / 24 / 64 (the source's); SMA 8 and BB x 2 fixed.

## Ambiguities resolved

- The 64-bar look-back window includes the current bar (`for i = 0 to 63`).
- Entry long = close short and the mirror: one-bar reversals (REVERSAL INTENDED).
- FREQ = "3h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
