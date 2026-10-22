# #442820 Moving Average Trading Strategy -> `fmz_442820_dip_under_30m_sma_unit_bracket_long`

- FMZ source id: 442820 (lineage).
- Source: https://www.fmz.com/strategy/442820 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-26 11:36:37). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C161). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry; the 30-minute value ends with the bar |
| 2 | ADAPT | Price-unit bracket -> fractions of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`dip` [0.99, 0.98] x `tp_frac` [0.002857, 0.01]: **4 trials**; the SMA length and the stop fraction fixed.

## Ambiguities resolved

- 30-minute value ends with the bar; price-unit bracket as fractions. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`coarse_bar_stop`
