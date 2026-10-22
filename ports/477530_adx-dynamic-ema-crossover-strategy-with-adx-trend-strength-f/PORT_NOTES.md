# #477530 动态指数均线交叉策略结合ADX趋势强度过滤系统-Dynamic-EMA-Crossover-Strategy-with-ADX-Trend-Strength-Filtering-System -> `fmz_477530_ema50_side_adx20_close_ratchet_reversal`

- FMZ source id: 477530 (lineage).
- Source: https://www.fmz.com/strategy/477530 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 11:44:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA side with an ADX filter and a close ratchet |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [50, 100] x `adx_threshold` [20.0, 25.0]: **4 trials**; DMI 20 / 20, 4 closes.

## Ambiguities resolved

- Ratchet cleared when the close is not above the entry price, as written; a same-side repeat on the close bar ends the trade.
- REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "adx_trend"`.

## Marks

`none`
