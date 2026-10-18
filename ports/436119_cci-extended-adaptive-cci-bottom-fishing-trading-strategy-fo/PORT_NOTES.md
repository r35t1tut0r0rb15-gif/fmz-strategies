# #436119 望远适应-CCI-底部捕捉商品交易策略Extended-Adaptive-CCI-Bottom-Fishing-Trading-Strategy-for-Commodities -> `fmz_436119_adaptive_cci_oversold_trail_long`

- FMZ source id: 436119 (lineage).
- Source: https://www.fmz.com/strategy/436119 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-21 14:30:03). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C86). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; trailing stop native |
| 2 | ADAPT | Price-unit trail -> percent trail |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity and the USD offset input quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`cci_length` [20, 30] x `trail_pct` [0.00025, 0.002]: **4 trials**; the eight adaptive levels and look-backs fixed.

## Ambiguities resolved

- Entry level never reset; price-unit trail -> percent trail (mark trailing_stop). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "cci_oscillator"`.

## Marks

`trailing_stop`
