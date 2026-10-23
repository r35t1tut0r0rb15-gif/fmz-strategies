# #438480 动量突破ATR波动率策略Momentum-Breakthrough-ATR-Volatility-Strategy -> `fmz_438480_sma50_200_cross_vwap_short_tick_bracket_1m_reversal`

- FMZ source id: 438480 (lineage).
- Source: https://www.fmz.com/strategy/438480 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-12 13:50:44). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed short-only tick bracket from the fill |
| 2 | PASS | SMA 50 / 200 crossings against the session VWAP |
| 3 | PASS | Exchange pair in the header only; tick distances converted at the source's BTC price. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; short bracket 1.14e-5 / 6.8e-6 of the fill.

## Ambiguities resolved

- Shared exit id: short-only bracket; ticks converted at the source's BTC price. Volume = broker tick volume (VWAP). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "vwap_breakout"`.

## Marks

`none`
