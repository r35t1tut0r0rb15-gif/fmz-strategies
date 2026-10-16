# #427994 Bollinger Bands Fibonacci Retracement Trading Strategy -> `fmz_427994_atr_fibo_band_straddle`

- FMZ source id: 427994 (lineage).
- Source: https://www.fmz.com/strategy/427994 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-27 16:52:05). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C15). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | ATR multiples only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 40] x `fibo` [1.618, 2.618]: **4 trials**; defaults 20 / 1.618 (the source's).

## Ambiguities resolved

- Defaults: Fibo 1 for both sides, reverse off; plot offset unused.
- A bar straddling both bands: the short (later order) wins. REVERSAL INTENDED. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_band_breakout"`.

## Marks

`none`
