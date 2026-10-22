# #440862 Dazzling Bolts Trend Following Strategy -> `fmz_440862_dazzling_bolts_bounce_bracket`

- FMZ source id: 440862 (lineage).
- Source: https://www.fmz.com/strategy/440862 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-02 17:30:09). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C141). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | PASS | Moving-average stack and ATR bracket |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Order size from the initial capital is sizing. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atrm` [2.0, 1.0] x `emalength` [55, 34]: **4 trials**; SMMA 10 and SMA 110 fixed.

## Ambiguities resolved

- Crossing closes as written; bracket from the signal close. Entries only from flat. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`coarse_bar_stop`
