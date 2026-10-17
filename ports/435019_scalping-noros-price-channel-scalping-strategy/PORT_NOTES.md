# #435019 诺罗波动通道scalping策略Noros-Price-Channel-Scalping-Strategy -> `fmz_435019_noro_bands_scalper_v10`

- FMZ source id: 435019 (lineage).
- Source: https://www.fmz.com/strategy/435019 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-11 17:06:27). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bar counts against a channel trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND426995. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 10]: **2 trials**.

## Ambiguities resolved

- qty-0 entries only close the opposite position; the entry price is the next open after the signal. REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_channel_breakout"`.

## Marks

`none`
