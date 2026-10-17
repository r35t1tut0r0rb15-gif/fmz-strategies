# #482872 双向MACD动量与EMA趋势判定交易策略-Bidirectional-MACD-Momentum-and-EMA-Trend-Trading-Strategy -> `fmz_482872_macd_zero_side_cross_ema200_bracket`

- FMZ source id: 482872 (lineage).
- Source: https://www.fmz.com/strategy/482872 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:58:38). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C laptop lane).
- Status: PORTED (batch L26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket from the signal bar (re-placement marked). |
| 2 | PASS | An EMA, MACD and percentage distances. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity quoted; the bracket via `stops()` and quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`operation` ["Long & Short", "Long"] x `tp_pct` [2.0, 3.0]: **4 trials**; defaults Long & Short / 2 (the source's);
EMA 200, MACD 12 / 26 / 9 and the 1 % stop fixed.

## Trailing stop (mark `trailing_stop_pending`)

A later same-side signal while held re-places the stop and target from the new close. The port keeps the entry's
bracket.

## Ambiguities resolved

- REVERSAL INTENDED. Stop module: `portfolio_kwargs` {} (D4). FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd"`.

## Marks

`trailing_stop_pending`
