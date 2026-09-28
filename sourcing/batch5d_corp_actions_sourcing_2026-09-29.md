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

## FDX (FedEx Corporation, NYSE, CIK 1048911)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2026-06-01 | Spinoff of FedEx Freight Holding Company (FDXF), 1 FDXF per 2 FDX, 80.1% distributed | **1.22624157** | sourced |

No splits, reverse splits or special cash distributions found for FDX in 2019-01-01..2026-09-28 (reading, based on the EDGAR 8-K item list from 2019 onward and the FY2026 10-K). The September 2026 424B5 filings are note offerings (5.750% Notes due 2036; EUR 4.000% 2030 / 4.625% 2034 notes), not equity events.

### Sources

**Form 8937** (signed June 22, 2026), linked from https://investors.fedex.com/fedex-freight-spin-off/default.aspx (that page is behind a Cloudflare challenge for curl; its content was fetched via WebFetch; the PDF itself downloaded directly):
https://s21.q4cdn.com/665674268/files/doc_downloads/2026/06/FedEx-Fairway-Form-8937-executed.pdf

> "On June 1, 2026, FedEx Corporation ("FedEx") distributed to holders of FedEx common stock, on a pro rata basis, 80.1% of the outstanding shares of FedEx Freight Holding Company, Inc. ("FedEx Freight") common stock (the "Distribution"). Each FedEx shareholder received one share of FedEx Freight common stock for every two shares of FedEx common stock held on May 15, 2026, the record date for the Distribution."

> "One method for determining the fair market values is to use the volume-weighted average trading prices of the FedEx common stock and the FedEx Freight common stock on June 1, 2026. Using this method, the fair market value of a share of FedEx common stock on June 1, 2026 was $336.39 and the fair market value of a share of FedEx Freight common stock on June 1, 2026 was $152.22. Based on these fair market values and the distribution ratio of one share of FedEx Freight common stock per two shares of FedEx common stock held, shareholders' pre-Distribution tax basis should be apportioned 81.55% to their FedEx common stock and 18.45% to their FedEx Freight common stock."

**8-K dated June 1, 2026** (Items 1.01, 2.01): https://www.sec.gov/Archives/edgar/data/1048911/000110465926068519/tm2616055d1_8k.htm

> "Each FedEx stockholder received one share of FedEx Freight common stock for every two shares of FedEx common stock held of record as of the close of business on May 15, 2026. Stockholders will receive cash in lieu of fractional shares. FedEx Freight will begin "regular way" trading on June 1, 2026 on the New York Stock Exchange ("NYSE") under the ticker symbol "FDXF.""

**Board approval release, Exhibit 99.4 to the May 13, 2026 8-K**: https://www.sec.gov/Archives/edgar/data/1048911/000110465926060233/tm2520565d14_ex99-4.htm

> "Beginning May 27, 2026 and ending at the close of business on May 29, 2026, it is expected that there will be two markets for FedEx common stock on the NYSE, a "regular-way" market and an "ex-distribution" market ... Shares of FedEx common stock that trade on the "regular-way" market beginning on the Record Date will trade under the symbol "FDX" with an entitlement to receive shares of FedEx Freight common stock in the distribution."

### Factor

v = 0.1845 (from the 8937). Factor = 1 / (1 - 0.1845) = 1 / 0.8155 = **1.22624157** (computed). Check: 0.5 x 152.22 / (336.39 + 0.5 x 152.22) = 76.11 / 412.50 = 0.18451 (computed).

### Gaps / caveats
- Ex date 2026-06-01 is my reading: regular-way FDX kept the entitlement through the 29 May close (a Friday), so 1 June was the first regular-way ex session. The OCC info memo #59055 ("FedEx Corporation - Distribution", 28 May 2026) returned HTTP 403 and was not read.
- The 8937 split uses **same-day post-spin VWAPs**, not the last cum close. That is the issuer's primary value split and the preferred source per the brief, but it is not identical to a price-based cum/ex ratio (reading).
- FedEx kept 19.9% of FDXF and plans to monetize it within 24 months, possibly by distributing it to FDX holders. No such event had been filed by 2026-09-28.

