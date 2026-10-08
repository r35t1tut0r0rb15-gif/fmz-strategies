# #426990 Bottom Following Trading Strategy -> `fmz_426990_noro_crypto_bottom_long`

- Source: https://www.fmz.com/strategy/426990 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-16 18:37:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A29). Not run.

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

`dist_mult` [2, 3] x `rsi_level` [10, 20]: **4 trials**, defaults 3 / 10 (the source's).

## Ambiguities resolved

- A qty-0 short entry is an exit (Noro's idiom); a bar with both signals ends flat. Long only.
- FREQ = "1h" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
