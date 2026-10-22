# #439207 Patient Trend Following Strategy -> `fmz_439207_patient_trendfollower_cci_pullback`

- FMZ source id: 439207 (lineage).
- Source: https://www.fmz.com/strategy/439207 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 12:40:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C118). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Tick target -> ATR multiple; price-unit spread -> fraction |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The capital / close order size and the pip inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND429967. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`k_tp` [1.0, 3.0] x `mult` [5.0, 3.0]: **4 trials**; EMA 21 / 55, CCI 20 level 1, ATR 55 and the spread fixed.

## Ambiguities resolved

- Tick target -> ATR multiple; level-1 setups only. Entries only from flat. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_confluence"`.

## Marks

`none`
