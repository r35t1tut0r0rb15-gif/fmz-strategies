# #446986 RSI和布林带双重策略RSI-and-Bollinger-Bands-Double-Strategy -> `fmz_446986_rsi_band_double_reentry_reversal`

- FMZ source id: 446986 (lineage).
- Source: https://www.fmz.com/strategy/446986 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-03 17:54:52). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C177). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Simultaneous RSI and band re-entries |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_len` [14, 7] x `bb_len` [20, 50]: **4 trials**; the levels and the multiplier fixed.

## Ambiguities resolved

- Cancels never act on market orders. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
