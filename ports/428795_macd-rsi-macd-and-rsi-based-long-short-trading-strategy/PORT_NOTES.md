# #428795 基于MACD和RSI的长短双向交易策略MACD-and-RSI-Based-Long-Short-Trading-Strategy -> `fmz_428795_macd_rsi_extreme_flag_bracket`

- FMZ source id: 428795 (lineage).
- Source: https://www.fmz.com/strategy/428795 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-09 15:33:17). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C20). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; the trail is a house trail (approximation stated). |
| 2 | ADAPT | Price-unit thresholds and tick distances -> ATR multiples. |
| 3 | PASS | "crypto" is in the name only; exchange pair in the header. |
| 4 | DONE | The exits are ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427239. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_atr` [0.4, 1.0] x `tp_atr` [1.7, 4.0]: **4 trials**; MACD / RSI thresholds, the trail (k 0.035, activation 0.115 %) and ATR 14 fixed.

## Ambiguities resolved

- tradeDirection = either extreme, as written. Inert close of a non-existent id.
- Trail: house volatility trail, approximation stated (mark trailing_stop). REVERSAL INTENDED. FREQ = "1h".
- Near-duplicate of #427239 (ND427239), which uses the EMA direction; this one uses the extreme flag.

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_momentum"`.

## Marks

`trailing_stop`
