# #451704 William Alligator Moving Average Trend Catcher Strategy -> `fmz_451704_alligator_ema200_alignment_from_flat`

- FMZ source id: 451704 (lineage).
- Source: https://www.fmz.com/strategy/451704 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-17 10:52:19). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C186). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Alligator alignment with an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity sizing and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`jaw` [8, 13] x `trend_len` [200, 100]: **4 trials**; teeth 5 and lips 3 fixed.

## Ambiguities resolved

- Flat for a bar between opposite trades. Entries only from flat. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
