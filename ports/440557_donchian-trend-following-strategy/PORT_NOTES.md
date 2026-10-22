# #440557 Donchian Trend Following Strategy -> `fmz_440557_donchian_close_channel_reversal`

- FMZ source id: 440557 (lineage).
- Source: https://www.fmz.com/strategy/440557 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-31 16:53:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C137). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Closing-price channel |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Risk-sized quantity, capital, commission and slippage settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG440557. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`big` [50, 20] x `small` [50, 10]: **4 trials**; the author's channel pairs.

## Ambiguities resolved

- Same-length exit channel reverses. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
