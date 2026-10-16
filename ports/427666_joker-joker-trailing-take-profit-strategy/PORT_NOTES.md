# #427666 Joker Trailing Take Profit Strategy -> `fmz_427666_joker_sma_cross_trail_tp`

- FMZ source id: 427666 (lineage).
- Source: https://www.fmz.com/strategy/427666 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-09-23 15:04:20). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C10). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close entries; trail as a house trail (approximation stated). |
| 2 | PASS | Percentages only. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 100 % of equity stored; exits quoted. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [23, 10] x `slow` [50, 100] x `tp_pct` [0.5, 1]: **8 trials**; defaults 23 / 50 / 0.5 (the source's); trail 0.01 % fixed.

## Trailing stop (FMZ-C rule 1, mark `trailing_stop`)

As written: `strategy.exit(trail_price = signal close x (1 +- 0.5 %), trail_offset = TP price x 0.01 % in ticks)`. Ported as the house trail `{"type": "percent", "pct": 0.0001, "anchor": "high_low", "activate_after": 0.005}`. **Stated approximation:** activation measured from the fill (next open) instead of the signal close; offset a percentage of the best price instead of fixed ticks. Promotion of a trailing trial needs the cTrader check (gate `trailing_ctrader_check`).

## Ambiguities resolved

- "Enable Trailing" fixed true. The short-side nz() typo is unreachable once short; ported without it.
- Date window dropped. Stop module: `portfolio_kwargs` `{}`; REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
