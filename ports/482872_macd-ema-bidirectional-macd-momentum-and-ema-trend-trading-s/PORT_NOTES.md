# #482872 双向MACD动量与EMA趋势判定交易策略-Bidirectional-MACD-Momentum-and-EMA-Trend-Trading-Strategy -> `fmz_482872_macd12_26_9_cross_beyond_zero_ema200_pct_bracket_reversal`

- FMZ source id: 482872 (lineage).
- Source: https://www.fmz.com/strategy/482872 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-20 15:58:38). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C252). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket as fractions of the fill |
| 2 | PASS | MACD crossings beyond zero with an EMA side |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [200, 100] x `tp_ratio` [2.0, 3.0]: **4 trials**; MACD 12 / 26 / 9, stop 1 %.

## Ambiguities resolved

- Operation type default Long & Short. A repeat signal's re-sent bracket is pending.
- MPL 2.0 source, ported and stated. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
