# #430009 Noros-值道策略v11Noros-Price-Channel-Strategy-v11 -> `fmz_430009_noro_price_channel_v11`

- FMZ source id: 430009 (lineage).
- Source: https://www.fmz.com/strategy/430009 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-24 10:59:38). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | A close channel, bar colours, body ratios and an RSI. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Lot = equity / close x leverage stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430009. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`pch` [30, 15, 60] x `rsi_limit` [25, 15]: **6 trials**; RSI period 2, body average 10 fixed.

## Ambiguities resolved

- Entry and exit on one bar: the bar ends flat (statement order).
- The unused channel trend is not ported. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "channel_reversal"`.

## Marks

`none`
