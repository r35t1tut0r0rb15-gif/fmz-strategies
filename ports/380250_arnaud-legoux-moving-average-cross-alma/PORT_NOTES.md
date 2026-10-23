# #380250 Arnaud Legoux Moving Average Cross ALMA -> `fmz_380250_alma60_120_cross_volume_osc_pct_bracket_flat_only`

- FMZ source id: 380250 (lineage).
- Source: https://www.fmz.com/strategy/380250 (PineScript v5, author Zer3192, FMZ last
  modified 2022-08-27 17:09:42). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V4). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; percent bracket from the fill |
| 2 | PASS | ALMA cross with a volume-oscillator filter |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG380250. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`alma1` [60, 30] x `alma2` [120, 90]: **4 trials**; TP 2 %, SL 2.5 %, volume EMA 5 / 10.

## Ambiguities resolved

- Flat follows the house bracket; the bracket starts on the fill bar. Volume = broker tick volume.
- FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_crossover"`.

## Marks

`coarse_bar_stop`
