# #426461 Noro's Fast RSI Breakthrough Strategy -> `fmz_426461_noro_fast_rsi_v16`

- Source: https://www.fmz.com/strategy/426461 (PineScript v2/v3, author ChaoZhang, FMZ last
  modified 2023-09-12 11:40:44). Verbatim here as `original_source.md`. Read 2026-10-07 (worker A).
- Status: PORTED (batch A27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Bar-derived quantities only. |
| 3 | PASS | Exchange pair in the header only (if any). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | Group `DG426461` (Jaccard >= 0.80) with #433396 (DUPLICATE); best Jaccard 0.854 with #433396. Group `ND426461` (Jaccard 0.65-0.80) with #436252 (PORT_CANDIDATE), #443238 (PORT_CANDIDATE); best Jaccard 0.761 with #436252. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [5, 7] x `limit` [20, 30]: **4 trials**, defaults 7 / 30 (the source's); body ratios, rule switches and bars fixed.

## Ambiguities resolved

- Re-read in A27: rejected in A19 as a pyramided ladder, but SURVEY_README classes pyramiding adds as sizing; the net position is ported.
- Average price = the position's first fill (adds are sizing).
- Orders fill in issue order; close_all closes whatever is open when it fills.
- Date window dropped; daily bars are broker days.

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks (2026-10-07)

`none`
