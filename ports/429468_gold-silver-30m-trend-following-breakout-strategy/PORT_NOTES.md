# #429468 Gold Silver 30m Trend Following Breakout Strategy -> `fmz_429468_rsi_dip_rip_ema162`

- FMZ source id: 429468 (lineage).
- Source: https://www.fmz.com/strategy/429468 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-10-17 14:11:47). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | RSI levels and a moving-average side. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() pyramiding 1 and commission stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_length` [14, 7] x `ema_length` [162, 100]: **4 trials**; OS 35 fixed (OB only feeds the inert exits).

## Ambiguities resolved

- Inert exits; the short uses the OS level as written. REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
