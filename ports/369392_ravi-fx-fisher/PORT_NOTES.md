# #369392 RAVI FX Fisher [Loxx] -> `fmz_369392_ravi_fisher_sign`

- Source: https://www.fmz.com/strategy/369392 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-06-16 15:15:28). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A16). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [4, 7] x `slow` [49, 65] = **4 trials**.

## Ambiguities resolved

- Fisher transform is tanh: its sign is the sign of maval. Trigger input unused.
- During warm-up fish is na, `fish >= 0` is false and the else branch enters short, as Pine does.
- Daily bars are broker days (17:00 New York), `FREQ = "1D"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks (2026-10-07)

`none`
