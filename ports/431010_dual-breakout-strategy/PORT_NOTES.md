# #431010 Dual Breakout Strategy -> `fmz_431010_bb_reentry_low_adx`

- FMZ source id: 431010 (lineage).
- Source: https://www.fmz.com/strategy/431010 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-03 17:16:02). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C43). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger bands and an ADX level |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity and the commission stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `adx_level` [30, 20]: **4 trials**; 2 sd, ADX 14 and DI 20 fixed.

## Ambiguities resolved

- Swing stop option off (default). REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
