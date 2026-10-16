# #429771 123 Reversal Moving Average Envelope Strategy -> `fmz_429771_combo_123_ma_envelope`

- FMZ source id: 429771 (lineage).
- Source: https://www.fmz.com/strategy/429771 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-20 16:05:43). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C28). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a percentage envelope. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426888. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length_ma` [18, 50] x `percent_shift` [0.2, 1.0]: **4 trials**; 123 settings fixed.

## Ambiguities resolved

- Disagreement closes all. REVERSAL INTENDED. FREQ = "4h".

## FAMILY (proposed, user to confirm)

`FAMILY = "combo_123_reversal"`.

## Marks

`none`
