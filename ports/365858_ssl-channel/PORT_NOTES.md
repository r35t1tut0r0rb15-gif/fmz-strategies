# #365858 SSL Channel -> `fmz_365858_ssl_channel_flip`

- Source: https://www.fmz.com/strategy/365858 (PineScript v5, author ChaoZhang, FMZ last
  modified 2022-05-26 12:19:48). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A14). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `ND365858` (Jaccard 0.65-0.80) with #391341 (PORT_CANDIDATE); best Jaccard 0.703 with #391341. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [10, 20, 50] = **3 trials**.

## Ambiguities resolved

- Orders use channel 2 (SMA 20); channel 1 (SMA 200) only draws.
- Wicks option default off (close compared).
- `FREQ = "45min"` from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_envelope_breakout"`.

## Marks (2026-10-07)

`none`
