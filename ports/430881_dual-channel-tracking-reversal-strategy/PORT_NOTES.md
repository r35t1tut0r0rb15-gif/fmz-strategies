# #430881 Dual Channel Tracking Reversal Strategy -> `fmz_430881_squeeze_momentum_roc`

- FMZ source id: 430881 (lineage).
- Source: https://www.fmz.com/strategy/430881 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-02 16:31:50). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C41). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed percentage stop |
| 2 | PASS | A regression momentum line and ROC |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`roc_len` [30, 60] x `pcnt` [7, 3]: **4 trials**; KC length 22 and the 100 % stop fixed.

## Ambiguities resolved

- The 100 % stop kept, the unreachable 5000 % target not emitted. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "momentum_oscillator_turn"`.

## Marks

`none`
