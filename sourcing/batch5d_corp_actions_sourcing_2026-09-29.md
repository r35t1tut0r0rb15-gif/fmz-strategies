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

## AIRF (Air France-KLM, Euronext Paris, ISIN FR0000031122 -> FR001400J770)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2021-04-19 (announced) | Capital increase **without** preferential subscription rights, EUR 4.84/share | 1 (no adjustment) | sourced |
| 2022-05-25 | Rights issue, 1 right -> 3 new shares at EUR 1.17 | **1.98275862** (variant b, recommended) / 2.20194772 (variant a) | sourced |
| 2023-08-31 | Reverse split 10 -> 1 | **0.1** | sourced |

### 2022-05-25 rights issue

**Source 1: issuer release, 24 May 2022** (PDF hosted on KLM's newsroom, linked from https://news.klm.com/rights-emission-air-france-klm/):
https://news.klm.com/download/1178189/20220524-afklm-rights-issue-en.pdf

> "Holders of existing ordinary shares of the Company (the "Shares") recorded on their accounts as of the end of the accounting day on 24 May 2022 will be entitled to receive Rights which will be detached from the underlying Shares on 25 May 2022. Existing Shares of the Company will therefore trade ex- right from 25 May, 2022. Each existing Share of the Company will entitle its holder to receive one (1) Right. 1 Right will entitle their holders to subscribe for 3 New Shares on an irreducible basis (à titre irréductible), at a subscription price of €1.17 per Share."

> "Based on the closing price of Air France-KLM stock on the regulated market of Euronext in Paris on 20 May 2022, i.e., €4.296, the theoretical value of 1 Right is €2.345 and the theoretical value of the ex-right share is €1.951."

The same text appears in the GlobeNewswire copy (fetched through WebFetch; direct curl got an empty reply): https://www.globenewswire.com/news-release/2022/05/24/2448880/0/en/Air-France-KLM-launches-a-2-256-billion-rights-issue-to-be-subscribed-in-cash-and-or-by-offsetting-claims.html

**Source 2: Eurex (Deutsche Börse) corporate-action notice**, issued 24 May 2022, effective 25 May 2022:
https://www.eurex.com/ex-en/rules-regs/corporate-actions/corporate-action-information/Air-France-KLM-SA-Rights-Issue-3094476

> "The company Air France-KLM SA announced a rights issue whereby shareholders are entitled to purchase 3 new shares for every 1 share held, at a subscription price of EUR 1.17 per new share. ... Adjustment result: Closing Price: EUR 3.45 R-Factor: 0.50434783 Options Adjusted contract size: AFR Version 0 100.0000 -> Version 1: 198.2759"

Procedure PDF: https://www.eurex.com/resource/blob/3094470/b14a62b587850a30a634bddf90d5094d/data/Info_001_AFR_en.pdf

> "Issue Date: Effective Date: 24 May 2022 25 May 2022"; "The official closing auction price of the on the last cum trading day will be the basis for determination of the R- factor. The R-factor will be determined with eight decimal places."

(The words "of the on the" are exactly as extracted; the PDF seems to have dropped a word.)

**(a) Issuer's own figure:** TERP EUR 1.951 from the **20 May 2022** close of EUR 4.296. Check: (4.296 + 3 x 1.17) / 4 = 1.9515 (computed), which matches. Factor = 4.296 / 1.951 = **2.20194772** (computed). This does *not* follow the convention, because 20 May was not the last cum-rights day (24 May was). Two trading days of price movement (4.296 -> 3.45) sit inside it.

**(b) From the official close on 24 May 2022:** EUR 3.45 (Eurex notice). TERP = (3.45 + 3 x 1.17) / 4 = 6.96 / 4 = **1.74** (computed). Factor = 3.45 / 1.74 = **1.98275862** (computed). Cross-check: 1 / 0.50434783 = 1.9827586 (computed), and Eurex's contract size 100 -> 198.2759 matches.

**Gaps:**
- The Eurex notice does not name the cash market. That EUR 3.45 is the **Euronext Paris** official close is my reading: Eurex bases the factor on the underlying's official closing auction price, and Euronext Paris is AF's primary listing.
- I could not fetch Euronext's own record. live.euronext.com returned an empty HTTP 202 (bot check); I did not try to get around it. The UniCredit/onemarkets notice for 24 May 2022 cites Euronext notice "CA220524DE4", which I could not find anywhere reachable: https://www.onemarkets.it/content/onemarkets-relaunch-it/it/info/announcements-and-notices/CorporateAction/2022.pdf?document=296039677.pdf
- The CSV carries variant (b) and puts (a) in the notes.

### 2023-08-31 reverse split (1:10)

Issuer release, 31 July 2023 (Nasdaq copy of the regulated release): https://www.nasdaq.com/press-release/terms-of-the-implementation-of-air-france-klm-reverse-share-split-2023-07-31

> "the reverse share split which starts today by means of an exchange of 10 existing shares for 1 new share, as decided by the Board of Directors at its meeting on 4 July 2023"

> "The shares subject to the reverse share split will be admitted to trading on the regulated market of Euronext Paris under ISIN code FR0000031122, until 30 August 2023, the last day of trading. The shares resulting from the reverse split will be admitted to trading on the regulated market of Euronext Paris from 31 August 2023, the first day of trading, and will be assigned ISIN code FR001400J770."

Issuer shareholder newsletter, July 2023: https://www.airfranceklm.com/sites/default/files/2023-07/Shareholders_Newsletter_july_2023.pdf

> "On 31 August 2023, existing Air France‑KLM shares will be converted into new shares at a parity of 10 to 1. For every 10 shares you own, you will receive 1 new share with a new ISIN code (FR001400J770)"

Factor = 1/10 = **0.1** (computed). Ex date / first trading day of new shares: 2023-08-31.

### 2021-04 capital increase (no rights)

https://www.nasdaq.com/press-release/air-france-klm-announces-the-success-of-its-capital-increase-2021-04-19

> "announces today the success of its capital increase without shareholders' preferential subscription rights, by way of a public offering and with a priority subscription period on an irreducible and reducible basis granted to existing shareholders"; "issuance of 213,999,999 new shares ... at a price per share of €4.84"

No tradeable right was detached, so there is no ex date and factor = 1 (reading). Listed only for completeness.

### Other AIRF notes
- airfranceklm.com HTML pages return a Cloudflare "Just a moment..." challenge, which I did not bypass. The /sites/default/files PDF above was directly downloadable.

