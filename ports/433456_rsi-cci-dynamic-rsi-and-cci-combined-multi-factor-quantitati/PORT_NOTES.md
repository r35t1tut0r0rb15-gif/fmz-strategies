# #433456 动态RSI与CCI结合的多因子量化交易策略Dynamic-RSI-and-CCI-Combined-Multi-factor-Quantitative-Trading-Strategy -> `fmz_433456_stoch_rsi_pullback_long`

- FMZ source id: 433456 (lineage).
- Source: https://www.fmz.com/strategy/433456 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-27 18:54:34). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C61). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Average order and oscillator levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The fund x leverage quantity and pyramiding 10 stored in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast_ma` [12, 24] x `slow_ma` [26, 52]: **4 trials**; the oscillator settings fixed.

## Ambiguities resolved

- Net position ported (pyramiding adds are sizing). Long only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
