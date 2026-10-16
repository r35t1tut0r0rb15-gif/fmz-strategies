# #429499 Moving Average Crossover Strategy -> `fmz_429499_sma9_21_cross_bracket_long`

- FMZ source id: 429499 (lineage).
- Source: https://www.fmz.com/strategy/429499 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 16:46:57). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C26). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry. |
| 2 | PASS | Moving-average crosses and percentages. |
| 3 | PASS | "Crypto" in the title only; exchange pair in the header. |
| 4 | DONE | The bracket is ported via stops() and quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [1.0, 2.0] x `tp_pct` [1.0, 2.0]: **4 trials**; SMA 9 / 21 fixed.

## Ambiguities resolved

- Bracket re-based on the fill. Long only. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
