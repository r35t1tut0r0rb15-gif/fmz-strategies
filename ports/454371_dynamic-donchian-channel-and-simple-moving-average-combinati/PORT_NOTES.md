# #454371 Dynamic Donchian Channel and Simple Moving Average Combination Quantitative Strategy -> `fmz_454371_donchian20_touch_sma200_side_reversal`

- FMZ source id: 454371 (lineage).
- Source: https://www.fmz.com/strategy/454371 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 17:29:48). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Donchian touches with an SMA filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50] x `sma_len` [200, 100]: **4 trials**; the offset 1 fixed.

## Ambiguities resolved

- Call order. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
