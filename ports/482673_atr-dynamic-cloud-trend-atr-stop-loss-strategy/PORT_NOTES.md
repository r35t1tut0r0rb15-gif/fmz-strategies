# #482673 动态波云趋势ATR止损策略-Dynamic-Cloud-Trend-ATR-Stop-Loss-Strategy -> `fmz_482673_tenkan_kijun_cross_cloud_lag26_atr_stop_reversal`

- FMZ source id: 482673 (lineage).
- Source: https://www.fmz.com/strategy/482673 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-27 17:54:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C248). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR stop as a fraction of the fill |
| 2 | PASS | Tenkan / Kijun crossings with cloud and lag filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [1.5, 3.0] x `displacement` [26, 52]: **4 trials**; Tenkan 9, Kijun 26, Span B 52, ATR 14.

## Ambiguities resolved

- Undisplaced spans, as written. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
