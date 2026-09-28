# Batch 5d: corporate-action adjustment factor sourcing

- Date checked: 2026-09-29 (session run on 2026-09-28/29 UTC)
- Checked by: claude-code-cloud
- Window: 2019-01-01 to 2026-09-28
- Factor convention: the loader DIVIDES pre-event prices by the factor.
  - split r:1 -> factor r
  - reverse split 1:k -> factor 1/k
  - distribution or spinoff worth fraction v of the pre-event price -> factor 1/(1-v)
  - rights issue -> factor = last cum-rights close / theoretical ex-right price (TERP)
- Labels: "(computed)" = my arithmetic on sourced inputs; "(reading)" = my interpretation.
- Every factor below comes from a fetched primary source with a verbatim quote. Where no exact factor could be sourced, the event is marked `unsourceable`.

## Access notes

- SEC EDGAR (www.sec.gov, efts.sec.gov): reachable.
- web.archive.org: connections reset by the session's egress proxy at the start of the session (tunnel closed mid-exchange). Retried later per symbol; see each section.

