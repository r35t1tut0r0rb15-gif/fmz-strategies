# #454356 基于RSIMACD布林带和成交量的混合交易策略RSI-MACD-Bollinger-Bands-and-Volume-Based-Hybrid-Trading-Strategy -> `fmz_454356_rsi_macd_bb_volume_spike_liquidity_zone_1h_long_only`

- FMZ source id: 454356 (lineage).
- Source: https://www.fmz.com/strategy/454356 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 15:54:04). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V31). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three alternative oversold / breakout / volume-spike entries with mirrored exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 10 % of equity, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`spike` [1.5, 2.0] x `zone` [50, 100]: **4 trials**; RSI 14, MACD 12 / 26 / 9, BB 20 x 2, SMA 50 / 200.

## Ambiguities resolved

- Flags reduce to a long / flat toggle. Volume = broker tick volume. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
