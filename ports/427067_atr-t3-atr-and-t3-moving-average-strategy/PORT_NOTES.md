# #427067 ATR and T3 Moving Average Strategy -> `fmz_427067_atr_t3_long`

- FMZ source id: 427067 (lineage).
- Source: https://www.fmz.com/strategy/427067 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-09-17 18:30:48). Verbatim here as `original_source.md`. Read 2026-10-15 (FMZ-C).
- Status: PORTED (batch C1). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | 5 % envelope around T3 -> `env_atr` x Wilder ATR(14). |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`t3_length` [25, 15] x `factor` [5, 3] x `env_atr` [10, 20, 35]: **12 trials**; defaults 25 / 5 / 20; T3 factor 0.72, ATR periods 5 and 1, the 1 x ATR(1) line fixed.

## Ambiguities resolved

- 5 % of price on 5-minute bars is tens of ATRs; the ATR grid brackets that width (judgement, stated before any backtest).
- Shorts are off by default: long only.
- Entries only from flat; one signal per bar.
- FREQ = "5min" from the backtest header.

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
