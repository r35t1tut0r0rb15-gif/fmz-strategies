# #433922 双指标组合疯狂日内scalping策略Dual-Indicators-Combo-Crazy-Intraday-Scalping-Strategy -> `fmz_433922_tmo_ama_scalper`

- FMZ source id: 433922 (lineage).
- Source: https://www.fmz.com/strategy/433922 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-01 14:47:57). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C63). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry |
| 2 | PASS | Oscillator divergences, a band regime and a swing-distance stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ama_len` [50, 100] x `sl_len` [10, 20]: **4 trials**; TMO 7, factor 2 and the kernel shape fixed.

## Ambiguities resolved

- Swing-distance stop re-based on the fill; flat-only entries tracked on bar highs / lows. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
