# #430893 Lion Fissure Balance Strategy -> `fmz_430893_jaws_mean_reversion_long`

- FMZ source id: 430893 (lineage).
- Source: https://www.fmz.com/strategy/430893 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-11-02 16:55:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; close-checked exits |
| 2 | PASS | SMA ratio, percentage target and a bar count |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The commented-out 5 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`big_len` [8, 20] x `pct_below` [1.0, 2.0]: **4 trials**; SMA 2, the 1 % target and 7 bars fixed.

## Ambiguities resolved

- Close-checked 1 % target from the fill price (default size 1). Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_reversion"`.

## Marks

`none`
