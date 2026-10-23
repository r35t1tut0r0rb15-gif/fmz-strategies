# #441047 MACD-量能反转交易策略MACD-Volume-Reversal-Trading-Strategy -> `fmz_441047_macd3_10_16_cross_contrarian_volume_10pct_target_1h_reversal`

- FMZ source id: 441047 (lineage).
- Source: https://www.fmz.com/strategy/441047 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-05 10:26:23). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 10 % target from the fill |
| 2 | PASS | MACD signal crossings on rising volume, traded contrarian |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`take_profit` [0.10, 0.03] x `slow` [10, 26]: **4 trials**; MACD fast 3, signal 16, volume multiplier 1.

## Ambiguities resolved

- Contrarian sides as written; fixed 10 % target. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_variant"`.

## Marks

`none`
