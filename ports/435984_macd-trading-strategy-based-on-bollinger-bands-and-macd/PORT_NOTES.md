# #435984 基于布林带和MACD的量化交易策略Trading-Strategy-Based-on-Bollinger-Bands-and-MACD -> `fmz_435984_boll_macd_rebound_atr_ratchet`

- FMZ source id: 435984 (lineage).
- Source: https://www.fmz.com/strategy/435984 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-20 15:55:18). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C84). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; exits on closes |
| 2 | PASS | Band touch, MACD and an ATR ratchet |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multi` [2, 3] x `boll_len` [20, 30]: **4 trials**; ATR 26, MACD 12 / 26 / 9 and the 2 sd width fixed.

## Ambiguities resolved

- Close-based ratchet exits; entry only from flat; bar_count rule as written. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
