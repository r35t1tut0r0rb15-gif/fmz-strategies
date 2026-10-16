# #430849 Triple Moving Average Trading Strategy -> `fmz_430849_triple_sma_crosses_long`

- FMZ source id: 430849 (lineage).
- Source: https://www.fmz.com/strategy/430849 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 14:47:45). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C40). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry (the shared-id re-binding approximated). |
| 2 | PASS | Moving-average crosses and percentage exits. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity per entry stored; the exits quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430849. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`tp_pct` [30.0, 10.0] x `sl_pct` [15.0, 5.0]: **4 trials**; SMA 50 / 100 / 200 fixed.

## Ambiguities resolved

- Trade named by its first cross; closes only on that pair. Shared exit id re-binding not modelled (approximation).
- Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
