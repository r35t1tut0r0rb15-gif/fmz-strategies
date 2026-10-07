# Near-duplicates: what "DUPLICATE 251 in 269 groups" means, and the candidate check (2026-10-07)

Worker A, branch `survey`. Static text comparison only.

## (a) "DUPLICATE 251" vs "269 groups"

The two numbers count different things.

- **269 groups**: `screen.py` grouped all 5,806 files (any outcome) by code similarity:
  5-token shingles of normalised code, exact Jaccard >= 0.80, same language, union-find.
  269 groups hold 596 files: 269 representatives + **327 collapsed members**.
- **DUPLICATE 251** is an *overall outcome*, and the overall outcome is assigned by priority:
  `FLAGGED_CRYPTO_ONLY` > `REJECTED` > `DUPLICATE` > `HELD_NEEDS_VOLUME` > `PORT_CANDIDATE`.
  A collapsed member that is also flagged or fails criterion 1/2 is counted under that outcome
  instead. So the 327 collapsed members split:

| Outcome of a collapsed member | Files |
|---|---:|
| DUPLICATE | 251 |
| REJECTED (fails criterion 1 or 2 itself) | 61 |
| FLAGGED_CRYPTO_ONLY | 15 |
| **Total collapsed** | **327** |

- The 251 DUPLICATE rows sit in 200 of the 269 groups; the other 69 groups contain only
  rejected/flagged collapsed members. All 251 are PineScript.
- Representatives of the 269 groups: 186 PORT_CANDIDATE, 47 REJECTED, 21 HELD_NEEDS_VOLUME,
  15 FLAGGED_CRYPTO_ONLY. (The representative is the member with the best screening status,
  then the lowest id, so a rejected representative means every member failed.)
- **How exact are the 251?** Compared with their representative (comment-stripped code):
  7 are exact copies (identical after removing all whitespace); 45 differ only in numbers,
  strings or cosmetic arguments (shingle Jaccard 1.00); the rest are 0.80-0.99 similar
  (59 at 0.80-0.85, 47 at 0.85-0.90, 50 at 0.90-0.95, 37 at 0.95-1.00), and 6 are below 0.80
  to the representative itself, joined through a chain of >= 0.80 pairs.

**Consequence of rule 7 (2026-10-07)**: "near-duplicates are still ported, exact duplicates stay
set aside". By the exact-copy test above, **244 of the 251 DUPLICATE rows are near-duplicates, not
exact copies**, so under rule 7 they should be ported, with group id `DG<representative>`. They are
not `PORT_CANDIDATE` rows, so neither worker's queue (Task 4 ports `PORT_CANDIDATE` ids) includes
them. **Decision owed**: re-open the 244 as candidates (each in its id's half), or keep them set
aside. Until decided, worker A does not port them. Their rows, with `exact_duplicate_of`, are in
`near_duplicate_groups.csv` (kind `near_duplicate_ge_0.80`).

## (b) Near-duplicate check over all 3,747 remaining PORT_CANDIDATE rows

Script: `survey_tools/near_dup_candidates.py` (deterministic). Output: `near_duplicate_groups.csv`,
both halves (A < 439378 <= B).

Method: same normalisation as the screen (comments removed, strings -> S, plot/label/alert/fill
lines and cosmetic keyword arguments removed, numbers -> 0), 5-token shingles, **exact Jaccard for
every same-language pair** of the 3,747 candidates that can reach 0.65 (pairs whose shingle-set
size ratio is below 0.65 cannot, and are skipped without loss): 3,127,289 pairs compared.
No pruning by common shingles (the screen pruned boiler-plate shingles; this check does not).

Results:

| Finding | Count |
|---|---:|
| Candidate pairs at Jaccard >= 0.80 (near-duplicate) | **0** |
| Exact duplicates among candidates | 0 |
| Groups at 0.65-0.80 (union-find, kind `similar_0.65_to_0.80`, id `ND<lowest id>`) | 124 groups, 302 candidates |
| ... of which span both halves (A and B) | 31 |
| Screen groups (kind `near_duplicate_ge_0.80`, id `DG<rep>`), all members listed | 269 groups, 596 rows |

Zero pairs at >= 0.80 is expected: the screen already merged every such pair and only the
representative stayed a candidate. The exhaustive run confirms the screen's pruning missed none
among candidates.

How a port uses it: `PORT_NOTES.md` quotes the port's `DG` group (if it represents one) and its
`ND` group (if any), with the partner ids. Nothing is collapsed by the `ND` band.
