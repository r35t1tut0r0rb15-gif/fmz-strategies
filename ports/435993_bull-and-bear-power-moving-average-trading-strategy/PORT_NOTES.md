# #435993 Bull and Bear Power Moving Average Trading Strategy -> `fmz_435993_bull_power_fade_percent_bracket`

- FMZ source id: 435993 (lineage).
- Source: https://www.fmz.com/strategy/435993 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-20 16:30:02). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C85). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; bracket fixed at entry |
| 2 | ADAPT | Price-unit trigger -> fraction of the close |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`reverse` [True, False] x `trigger_frac` [0.005, 0.01]: **4 trials**; EMA 14 and the 7 % bracket fixed.

## Ambiguities resolved

- Day high restarts at 00:00 UTC; price-unit trigger -> fraction; entry from flat. Opposite entries cannot occur. FREQ = "30min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
