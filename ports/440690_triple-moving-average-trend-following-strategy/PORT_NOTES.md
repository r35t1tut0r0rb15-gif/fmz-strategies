# #440690 Triple Moving Average Trend Following Strategy -> `fmz_440690_triple_sma_cross_flat_first`

- FMZ source id: 440690 (lineage).
- Source: https://www.fmz.com/strategy/440690 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-01 11:02:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C138). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a slow filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1, capital, commission and slippage settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [8, 5] x `slow` [55, 100]: **4 trials**; the medium SMA 21 fixed.

## Ambiguities resolved

- Opposite signal flattens (close_all after the entry). FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
