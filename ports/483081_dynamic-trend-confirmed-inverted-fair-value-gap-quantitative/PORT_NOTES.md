# #483081 动态趋势确认的反转公平价值缺口量化交易策略-Dynamic-Trend-Confirmed-Inverted-Fair-Value-Gap-Quantitative-Trading-Strategy -> `fmz_483081_inverted_fvg_fade_sma_trend_reversal`

- FMZ source id: 483081 (lineage).
- Source: https://www.fmz.com/strategy/483081 (PineScript v6, author ianzeng123, FMZ last
  modified 2025-02-21 11:55:42). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L21). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Gap bars and moving averages; the price-unit exits are inert and dropped. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing in the source; the inert exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [50, 20] x `slow` [200, 100]: **4 trials**; defaults 50 / 200 (the source's).

## Price-unit exits (criterion 2)

The stop (100 points), the 3 R target (300) and the trail that starts 50 points in profit are price units. On
SOL_USDT 2-minute bars (price about 150-250 USD, ATR about 0.3 USD) none can be reached in a trade: dropped as inert (as
#492009, #490798). The port is a stop-and-reverse on the entries.

## Ambiguities resolved

- `fvg` / `ifvg` are `var` flags only ever set: true for good after the first gap / break, as written; the recorded
  levels change on every qualifying break (na on the other side).
- REVERSAL INTENDED; no exits or stops. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "price_action"`.

## Marks

`none`
