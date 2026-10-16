# #428683 Trix Simple Trend Following Strategy -> `fmz_428683_trix_simple`

- FMZ source id: 428683 (lineage).
- Source: https://www.fmz.com/strategy/428683 (PineScript v3, author ChaoZhang, FMZ last
  modified 2023-10-08 12:17:21). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Log-price oscillators and MA lengths. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lengtha` [7, 14] x `lengtha1` [4, 2]: **4 trials**; defaults 7 / 4 (the source's); band 20, SMAs 13 / 68 fixed.

## Ambiguities resolved

- The exits carry no price (inert): positions change only on the opposite entry. "ema13" is an SMA as written.
- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trix"`.

## Marks

`none`
