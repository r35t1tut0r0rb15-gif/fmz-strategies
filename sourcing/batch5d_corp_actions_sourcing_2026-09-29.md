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

## IBM (International Business Machines, NYSE, CIK 51143)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2021-11-04 | Spinoff of Kyndryl Holdings (KD), 1 KD per 5 IBM, 80.1% distributed | **1.04384134** | sourced |

No splits, reverse splits or other special distributions found for IBM in the window (reading, based on the 8-K item lists). IBM kept 19.9% of Kyndryl and planned to exchange it for IBM debt. That was not a distribution to IBM holders, so it needs no price adjustment (reading).

### Sources

**IBM Form 8937**, linked as "Download IRS Form 8937" from https://www.ibm.com/investor/services/faqs-about-the-kyndryl-holdings-inc-distribution:
https://www.ibm.com/investor/att/pdf/Form-8937-Report-of-Organizational-Actions-Affecting-Basis-of-Securities.pdf

The PDF is a scanned image with no text layer. I rendered its pages to images and transcribed the text below by reading those images.

> Line 14: "On November 3, 2021, IBM distributed 80.1% of the outstanding shares of Kyndryl Holdings to IBM common stockholders. Each holder of IBM common stock received one share of Kyndryl Holdings common stock for every five shares of IBM common stock held as of the record date, October 25, 2021."

> Line 15: "One possible approach is to utilize the New York Stock Exchange market closing price on November 4, 2021, the date on which Kyndryl Holdings stock first traded, (the "Closing Price") as an indication of the fair market value. For IBM common stock the Closing Price was $120.85 per share and for Kyndryl Holdings common stock the Closing Price was $26.38 per share. Based on that approach and the assumptions and calculations set forth in Line 16 below, 95.8% of an IBM stockholder's aggregate tax basis in shares of IBM common stock immediately prior to the Distribution would be allocated to such shareholder's shares of IBM common stock and 4.2% would be allocated to such shareholder's shares of Kyndryl Holdings common stock received in the Distribution"

**IBM 8-K, November 3, 2021** (Item 2.01): https://www.sec.gov/Archives/edgar/data/51143/000155837021014643/ibm-20211103x8k.htm

> "The distribution was made in the amount of one share of Kyndryl common stock for every five shares of IBM common stock (the "Distribution") owned by IBM's stockholders of record as of the close of business on October 25, 2021."

**Board approval release, October 12, 2021** (8-K Ex. 99.1): https://www.sec.gov/Archives/edgar/data/51143/000110465921125064/tm2128856d3_ex99-1.htm

> "The distribution is expected to occur after close of market on November 3, 2021."

**IBM FAQ page:** "The distribution was effective as of 5:00 PM, Eastern time, on 3 November 2021."

### Factor

v = 0.042 (issuer, rounded). Factor = 1 / 0.958 = **1.04384134** (computed). Unrounded from the issuer's own closing prices: v = 5.276 / 126.126 = 0.041831, factor = 1.04365737 (computed). The difference is about 0.02%.

### Gaps
- Ex date 2021-11-04 is my reading, based on the after-close distribution on 3 Nov and KD's first trade on 4 Nov. No exchange notice was fetched.
- The Kyndryl IR spinoff page (investors.kyndryl.com) returned 403 to curl and 503 to WebFetch. It wasn't needed.

## T (AT&T Inc., NYSE, CIK 732717)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2022-04-11 | WarnerMedia spinoff + merger with Discovery (Reverse Morris Trust): 1 SpinCo per T share -> 0.241917 WBD | **1.30684788** | sourced |

No splits, reverse splits or other special distributions found for T in the window (reading, based on the 8-K item lists).

### Sources

**AT&T attachment to Form 8937**: https://investors.att.com/~/media/Files/A/ATT-IR-V2/documents/attachment-to-form-8937-new.pdf

> Line 14: "At the close of business on April 8, 2022, AT&T completed the previously announced transaction to combine AT&T's WarnerMedia business with Discovery by distributing, on a pro rata basis, all of the outstanding common stock of SpinCo to AT&T common stockholders of record as of April 5, 2022 (the "Distribution"). Pursuant to the Distribution, each holder of AT&T common stock received one share of SpinCo common stock for every share of AT&T common stock held as of the record date. ... In the Merger, each share of SpinCo common stock immediately prior to the Merger was automatically converted into the right to receive 0.241917 shares of WBD common stock."

> Line 16: "One approach to determine the fair market value of AT&T is to use the average of the opening and closing trading prices quoted on the New York Stock Exchange on April 11, 2022, the first trading day following the Distribution. ... Using the average of the opening and closing trading prices for shares of WBD common stock ($24.43) and shares of AT&T common stock ($19.26) on April 11, 2022, and taking into account the Merger exchange ratio (1 : 0.241917 SpinCo to WBD), approximately 23.48% of the aggregate tax basis held by the AT&T stockholders immediately prior to the Distribution would be allocated to the shares of SpinCo common stock received by such stockholders."

**AT&T 8-K, April 8, 2022**: https://www.sec.gov/Archives/edgar/data/732717/000073271722000030/t-20220408.htm

> "each holder of shares of common stock, par value $1.00 per share, of AT&T (the "AT&T Common Stock") was entitled to receive one share of Spinco Common Stock for each share of AT&T Common Stock held as of the record date, April 5, 2022 ... the holders of Spinco Common Stock were entitled to receive 0.241917 shares of WBD common stock (the "Exchange Ratio") for each share of Spinco Common Stock held on the closing date."

### Factor

v = 0.2348. Factor = 1 / 0.7652 = **1.30684788** (computed). Check: 0.241917 x 24.43 = 5.9100; 5.9100 / (19.26 + 5.9100) = 0.23480 (computed).

### Gaps
- Ex date 2022-04-11 is my reading (distribution at the close on Friday 8 April; the 8937 names 11 April as "the first trading day following the Distribution"). No NYSE ex-date notice was fetched.
- The 8937 values are the average of open and close on 11 April, not the last cum close. That is the issuer's method.

## GE (General Electric, now GE Aerospace, NYSE, CIK 40545)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2019-02-26 | GE Transportation spin + merger into Wabtec: 0.005371 WAB per GE share (taxable dividend) | none: needs GE cum close | **unsourceable** |
| 2021-08-02 | Reverse split 1:8 | **0.125** | sourced |
| 2023-01-04 | Spinoff of GE HealthCare (GEHC), 1 per 3, ~80.1% distributed | **1.26374321** | sourced |
| 2024-04-02 | Spinoff of GE Vernova (GEV), 1 per 4, 100% distributed | **1.25407575** | sourced |

The brief mentioned "two spinoffs" (GEHC and GEV). The window also includes the Wabtec transaction and the reverse split. Other 8-Ks with Item 2.01 (Baker Hughes deconsolidation 2019-09, BioPharma sale 2020-04, GECAS sale 2021-11) were asset sales, not shareholder distributions (reading). The 2026-06-25 Item 5.03 8-K is a bylaw amendment.

### 2019 Wabtec transaction (unsourceable factor)

GE Shareholder Services page: https://www.ge.com/investor-relations/shareholder-services

> "On February 25th, 2019, GE completed the spin-off and subsequent merger of its transportation business with Wabtec Corporation (NYSE:WAB). Under the terms of the transaction, GE distributed all 8.7 billion shares of common stock of Transportation Systems Holdings Inc. ("SpinCo") with respect to the shares of GE common stock outstanding as of the close of business on February 14, 2019 by means of a pro rata distribution (the "Spin-off"), and SpinCo and a subsidiary of Wabtec then merged. Record Date: GE shareholders must own GE stock by February 14th and hold through February 25th close of trade to be eligible to receive Wabtec shares. Exchange ratio: GE shareholders receive .005371 shares of Wabtec for every 1 share of GE owned. ... Fair Market Value: $78.06 per share, the closing stock price of Wabtec on February 25, 2019. ... Cost Basis Adjustment to GE Shares: No change to historic cost basis of GE shares. ... GE will not be filing form 8937 because the transaction has no impact on the tax basis in GE shares."

- Value distributed per GE share = 0.005371 x 78.06 = **$0.41926** (computed).
- **Why unsourceable:** there is no 8937 and no issuer-stated fraction. The factor needs GE's last cum close (2019-02-25), and I did not fetch that from a primary source. The factor would be C / (C - 0.41926) (computed formula), on the pre-reverse-split share basis.
- Ex date 2019-02-26 is my reading. "Hold through February 25th close of trade" implies due-bill trading, which puts the ex date on the next day.

### 2021-08-02 reverse split 1:8

8-K July 30, 2021 (Item 3.03): https://www.sec.gov/Archives/edgar/data/40545/000120677421001925/ge3936671-8k.htm

> "On July 30, 2021, General Electric Company (the "Company") filed a Certificate of Amendment to its Certificate of Incorporation (the "Certificate of Amendment") in order to effect a one-for-eight reverse stock split of the Company's common stock ... On August 2, 2021, GE common stock will begin trading, on a split-adjusted basis, (i) on the New York Stock Exchange under the symbol "GE", with a new CUSIP number (369604 301)"

The shareholder-services page adds: "GE filed an amendment to its certificate of incorporation to effectuate the reverse stock split after the close of trading on July 30, 2021, and GE common stock began trading on a split-adjusted basis on August 2, 2021."

Factor = 1/8 = **0.125** (computed).

### 2023-01-04 GE HealthCare spinoff

GE Form 8937 attachment: https://www.ge.com/sites/default/files/general-electric-form-8937-attachment.pdf

> "On January 3, 2023, after the close of trading on The Nasdaq Stock Market LLC, pursuant to the terms and conditions of the Separation and Distribution Agreement dated as of November 7, 2022, as amended, by and among GE and GEHC, GE distributed to its shareholders on a pro rata basis approximately 80.1 percent of its shares of GEHC common stock (the "Distribution"). Pursuant to the Distribution, each holder of record of GE common stock received one share of GEHC common stock for every three shares of GE common stock held on December 16, 2022"

> "One possible approach is to utilize the New York Stock Exchange opening trading price on January 4, 2023 for GE common stock ($68.41 per share) and the Nasdaq opening trading price for GEHC common stock ($54.13 per share) as an indication of the fair market value. Based on that approach ... 79.13% of a GE shareholder's aggregate tax basis ... would be allocated to such shareholder's shares of GE common stock following the Distribution, and 20.87% ... would be allocated to such shareholder's shares of GEHC common stock received in the Distribution."

8-K Jan 4, 2023: https://www.sec.gov/Archives/edgar/data/40545/000119312523001157/d431727d8k.htm ("On January 4, 2023, GE HealthCare's common stock began trading on The Nasdaq Stock Market LLC under the ticker symbol "GEHC."")

Factor = 1 / (1 - 0.2087) = **1.26374321** (computed). Check: (54.13/3) / (68.41 + 54.13/3) = 0.20871 (computed).

### 2024-04-02 GE Vernova spinoff

GE Form 8937 attachment (hosted on geaerospace.com): https://www.geaerospace.com/sites/default/files/ge-form-8937-attachment.pdf

> "On April 2, 2024, prior to the open of trading on the New York Stock Exchange, pursuant to the terms and conditions of the Separation and Distribution Agreement dated as of April 1, 2024, by and among GE and GEV, GE distributed to its shareholders on a pro rata basis 100 percent of its shares of GEV common stock (the "Distribution"). Pursuant to the Distribution, each holder of record of GE common stock received one share of GEV common stock for every four shares of GE common stock held on March 19, 2024"

> "One possible approach is to utilize the New York Stock Exchange opening trading price on April 2, 2024 for GE common stock ($140.53 per share) and the New York Stock Exchange opening trading price for GEV common stock ($142.85 per share) as an indication of the fair market value. Based on that approach ... 79.74% ... would be allocated to such shareholder's shares of GE common stock following the Distribution, and 20.26% ... would be allocated to such shareholder's shares of GEV common stock received in the Distribution."

8-K April 2, 2024: https://www.sec.gov/Archives/edgar/data/40545/000119312524084038/d792336d8k.htm ("On April 2, 2024 (the "Distribution Date") at 12:10 a.m. Eastern Time, General Electric Company completed the previously announced separation ...")

Factor = 1 / (1 - 0.2026) = **1.25407575** (computed). Check: (142.85/4) / (140.53 + 142.85/4) = 0.20263 (computed).

### Gaps
- Wabtec 2019: factor unsourceable (see above).
- Both spinoff ex dates are my readings from the distribution timing in the 8937s and 8-Ks. No NYSE ex-date notice was fetched.
- Both 8937s use **opening prices on the ex date**, not the last cum close.

## PFE (Pfizer Inc., NYSE, CIK 78003)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2020-11-17 | Upjohn spinoff + combination with Mylan -> Viatris (VTRS), ~0.124079 VTRS per PFE | none | **unsourceable** |

No splits, reverse splits or other special distributions found for PFE in the window (reading, based on the 8-K item lists). The 2019 consumer-health JV with GSK was not a shareholder distribution (reading).

### Sources fetched

**Pfizer 8-K, November 20, 2020** (Item 2.01): https://www.sec.gov/Archives/edgar/data/78003/000119312520298356/d72492d8k.htm

> "Effective as of 12:01 a.m. Eastern time on November 16, 2020, pursuant to the Separation and Distribution Agreement and the Business Combination Agreement, Pfizer completed the previously announced Separation of the Upjohn Business as a result of the Distribution and, after the Distribution, the combination of the Upjohn Business with Mylan. In the Distribution, Pfizer stockholders received approximately 0.124079 shares of common stock of Viatris for every one share of Pfizer common stock held by such Pfizer stockholder as of the close of business on the Record Date."

(Record date: "the record date of November 13, 2020".)

**Pfizer release, November 5, 2020** (8-K Ex. 99.1): https://www.sec.gov/Archives/edgar/data/78003/000119312520286896/d81265dex991.htm

> "If a Pfizer stockholder sells shares of Pfizer common stock in the "regular way" market beginning on November 12, 2020, the date that is the business day immediately prior to the record date for the spin-off, and continuing until the close of business on the expected closing date of November 16, 2020, that Pfizer stockholder will be selling both his or her shares of Pfizer common stock and the right (represented by a "due-bill") to receive shares of Viatris common stock in the distribution."

The ex date of 2020-11-17 is my reading: 16 Nov was the last regular-way day carrying the due bill.

### Why the factor is unsourceable
- The Form 8937 URL that search engines index, https://s21.q4cdn.com/317678438/files/doc_news/2020/08/Distribution-Tax-Basis-Information.pdf, returns **HTTP 404** (curl and WebFetch).
- pfizer.com investor pages return **403** (curl and WebFetch). investor.viatris.com returned an empty reply (curl) or 503 (WebFetch).
- **web.archive.org is blocked by this session's egress proxy** (connection reset). archive.org's availability API (reachable) lists a snapshot: `http://web.archive.org/web/20240616120847/https://s21.q4cdn.com/317678438/files/doc_news/2020/08/Distribution-Tax-Basis-Information.pdf`. A session with archive.org access can close this gap quickly.
- Search-engine summaries quote "94.8%" to Pfizer and "5.2%" to Viatris. **I did not fetch the document, so this figure is not used.** If confirmed, it would give 1/(1-0.052) = 1.05485232 (computed, **not sourced**).

## VOWG_p (Volkswagen AG preference shares, Xetra, ISIN DE0007664039)

### Events in window

| Ex date | Event | Factor | Status |
|---|---|---|---|
| 2022-12-19 | Special dividend EUR 19.06 per preference share (from the Porsche AG IPO proceeds), paid 2023-01-09 | **1.16224038** | sourced |

No splits, reverse splits, rights issues or spinoffs to shareholders found for VW preference shares in the window (reading). The Porsche AG IPO in Sept 2022 placed shares with investors and did not distribute them to VW holders; the cash went out through this special dividend. Ordinary annual dividends are out of scope.

### Sources

**Eurex corporate-action notice** (dated Dec 19, 2022): https://www.eurex.com/ex-en/rules-regs/corporate-actions/corporate-action-information/Volkswagen-AG-Preference-shares-Special-Dividend-3297074

> "The company Volkswagen AG has announced the payment of a special dividend of EUR 19.06 per share. ... The payment of the special dividend will result in an adjustment of the above-mentioned contracts. Volkswagen AG - - Preference shares : Special dividend adjustment result Adjustment result: Closing price: 136.54 R-Factor: 0.86040721"

Procedure PDF: https://www.eurex.com/resource/blob/3297072/153ed45408dc4b34595debc11412c7d6/data/Info_001_VOW3_en.pdf

> "Issue Date: 21 October 2022 Effective Date: 19 December 2022 ... Corporate Action Special Dividend Company ISIN ... Volkswagen AG – Preference shares DE0007664039"; "Determination of adjustment factor (R-factor) S1 S2 Closing auction price of the share S1 minus special dividend R-Factor S2 / S1"

**Volkswagen AG dividend notice (Dividendenbekanntmachung), 19 Dec 2022**: https://uploads.vw-mms.de/system/production/documents/cws/002/173/file_de/d3939780dfaefc7f9dc37b7fef0c10897a0390ee/2022-12-19_Volkswagen_AG_Dividendenbekanntmachung_Sonderdividende.pdf?1686563055=

> "Die außerordentliche Hauptversammlung unserer Gesellschaft hat am 16. Dezember 2022 beschlossen, ... 9.554.687.712,78 Euro zur Zahlung einer Sonderdividende von 19,06 Euro je dividendenberechtigter Stammaktie und je dividendenberechtigter Vorzugsaktie ... Zusätzlich hat die außerordentliche Hauptversammlung am 16. Dezember 2022 beschlossen, dass der Anspruch auf die Sonderdividende am 9. Januar 2023 fällig ist."

**VW media release No. 175/2022** (Dec 16, 2022): https://www.volkswagen-group.com/en/publications/more/press-release-vw-shareholders-approve-special-dividend-2152/download?disposition=attachment

> "approved a special distribution of EUR 19.06 per ordinary and preferred share entitled to dividend with a majority of 99,9974 percent ... the shareholders also voted in favor of the distribution of the special dividend on January 9, 2023."

### Factor

v = 19.06 / 136.54 = 0.139593 (computed). Factor = 1 / (1 - v) = 136.54 / 117.48 = **1.16224038** (computed). Cross-check: 117.48 / 136.54 = 0.86040721, which equals Eurex's R-factor (computed).

### Gaps / caveats
- **Ex date:** the issuer notice gives the payment date (9 Jan 2023) but no explicit ex date. I use Eurex's effective date of 19 Dec 2022, the first trading day after the Friday 16 Dec EGM. That this matches the Xetra cash ex date is my reading. The loader should confirm the price gap sits at 19 Dec and not at early January.
- That the 136.54 close is the Xetra closing auction of 16 Dec 2022 is my reading (Eurex says only "Closing auction price of the share").

## IBE (Iberdrola S.A., BME Mercado Continuo, ISIN ES0144580Y14)

### Events in window: 16 scrip editions ("Iberdrola Retribución Flexible")

Each edition is a free-share capital increase: 1 free-allocation right per share, and N rights convert into 1 new share. Holders can take new shares, sell the rights in the market, or take a cash dividend (Dividendo a Cuenta in January, Dividendo Complementario in July) by waiving their rights. All terms come from the official legal notice Iberdrola publishes in the BORME (Boletín Oficial del Registro Mercantil, Sección Segunda, "AUMENTO DE CAPITAL"), fetched from boe.es.

| Ex date (1st rights-trading day) | Last cum date (BORME publication) | Record date | Rights per new share N | Cash option EUR/share | Factor (N+1)/N (computed) | BORME ref |
|---|---|---|---|---|---|---|
| 2019-01-09 | 2019-01-08 | 10 de enero de 2019 | 45 | 0.151 (interim) | 1.02222222 | [BORME-C-2019-46](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2019-46) |
| 2019-07-04 | 2019-07-03 | 5 de julio de 2019 | 43 | 0.200 (final) | 1.02325581 | [BORME-C-2019-5647](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2019-5647) |
| 2020-01-09 | 2020-01-08 | 10 de enero de 2020 | 54 | 0.168 (interim) | 1.01851852 | [BORME-C-2020-63](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2020-63) |
| 2020-07-08 | 2020-07-07 | 9 de julio de 2020 | 44 | 0.232 (final) | 1.02272727 | [BORME-C-2020-3353](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2020-3353) |
| 2021-01-12 | 2021-01-11 | 13 de enero de 2021 | 70 | 0.168 (interim) | 1.01428571 | [BORME-C-2021-88](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2021-88) |
| 2021-07-08 | 2021-07-07 | 9 de julio de 2021 | 40 | 0.254 (final) | 1.02500000 | [BORME-C-2021-5035](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2021-5035) |
| 2022-01-10 | 2022-01-07 | 11 de enero de 2022 | 60 | 0.170 (interim) | 1.01666667 | [BORME-C-2022-67](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2022-67) |
| 2022-07-08 | 2022-07-07 | 11 de julio de 2022 | 36 | 0.274 (final) | 1.02777778 | [BORME-C-2022-4847](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2022-4847) |
| 2023-01-06 | 2023-01-05 | 9 de enero de 2023 | 60 | 0.180 (interim) | 1.01666667 | [BORME-C-2023-52](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2023-52) |
| 2023-07-07 | 2023-07-06 | 10 de julio de 2023 | 37 | 0.316 (final) | 1.02702703 | [BORME-C-2023-4566](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2023-4566) |
| 2024-01-09 | 2024-01-08 | 10 de enero de 2024 | 58 | 0.202 (interim) | 1.01724138 | [BORME-C-2024-71](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2024-71) |
| 2024-07-04 | 2024-07-03 | 5 de julio de 2024 | 34 | 0.351 (final) | 1.02941176 | [BORME-C-2024-4108](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2024-4108) |
| 2025-01-10 | 2025-01-09 | 13 de enero de 2025 | 58 | 0.231 (interim) | 1.01724138 | [BORME-C-2025-39](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2025-39) |
| 2025-07-04 | 2025-07-03 | 7 de julio de 2025 | 39 | 0.409 (final) | 1.02564103 | [BORME-C-2025-3945](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2025-3945) |
| 2026-01-12 | 2026-01-09 | 13 de enero de 2026 | 73 | 0.253 (interim) | 1.01369863 | [BORME-C-2026-65](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2026-65) |
| 2026-07-06 | 2026-07-03 | 7 de julio de 2026 | 50 | 0.425 (final) | 1.02000000 | [BORME-C-2026-3939](https://www.boe.es/diario_borme/txt.php?id=BORME-C-2026-3939) |

Every row is `sourced` for the ratio, dates and cash amount. The **factor treatment is my reading** (see the decision below).

### Verbatim quotes (pattern shared by all 16 notices; per-edition numbers are in the CSV `source_quote`)

BORME-C-2019-46 (8 Jan 2019): https://www.boe.es/diario_borme/txt.php?id=BORME-C-2019-46

> "gozarán del derecho de asignación gratuita de las nuevas acciones, en la proporción de una acción nueva por cada 45 derechos de asignación gratuita, los accionistas de la Sociedad: (a) que hayan adquirido sus respectivas acciones de Iberdrola no más tarde de las 23:59 horas de Madrid del día de publicación de este anuncio (last trading date); y (b) cuyas operaciones bursátiles se hayan liquidado hasta el día 10 de enero de 2019 (record date) en los registros contables de Iberclear. A cada acción antigua de la Sociedad le corresponderá un derecho de asignación gratuita."

> "los derechos de asignación gratuita serán negociables en las Bolsas de Valores de Bilbao, Madrid, Barcelona y Valencia ... durante un plazo de 15 días naturales, a partir del día natural siguiente al de la publicación de este anuncio (esto es, entre el 9 y el 23 de enero de 2019, ambos inclusive)."

> "Por tanto, el importe bruto por acción del Dividendo a Cuenta también ascenderá a 0,151 euros."

BORME-C-2026-3939 (3 Jul 2026): https://www.boe.es/diario_borme/txt.php?id=BORME-C-2026-3939

> "en la proporción de una acción nueva por cada 50 derechos de asignación gratuita ... no más tarde de las 23:59 horas de Madrid del día de publicación de este anuncio (last trading date); y (b) cuyas operaciones bursátiles se hayan liquidado hasta el día 7 de julio de 2026 (record date)"

> "a partir del día hábil bursátil siguiente al de la publicación de este anuncio (esto es, entre el 6 y el 20 de julio de 2026, ambos inclusive)."

> "(i) el importe bruto por acción del Dividendo Complementario es de 0,425 euros; y (ii) el importe bruto por acción del Dividendo de Ajuste es de 0,002 euros."

### Factor treatment (reading, needs a decision)

The brief's convention has no rule for a scrip. I treat each edition as a **bonus issue of 1 new share per N held**, i.e. a split of (N+1):N, so factor = (N+1)/N (computed from the sourced N). This is how a free-share ("liberada") capital increase is usually adjusted. It fits the economics: N is set so that a right is worth about the cash option. An alternative is to treat each edition as a **cash dividend equal to the cash option**, factor = C/(C - cash), where C is the last cum close. That needs a sourced close, which I did not fetch. The two treatments differ only slightly (reading).

### Other IBE events checked
- **July 2025 EUR 5bn capital increase**: an accelerated placement **without** preferential subscription rights (per Iberdrola's newsroom headline "Iberdrola culmina con éxito la ampliación de capital de 5.000 millones de euros, sobresuscrita en 3,8 veces", seen in search results only; iberdrola.com returns 403 and was not fetched). No rights were detached, so there is no factor (reading).
- Capital reductions that cancel buyback shares happen regularly. They change neither the per-share price nor the holdings, so no factor (reading).
- The EUR 0.002 "Dividendo de Ajuste" in July 2026 is paid on every share. It is ordinary-dividend size and ignored.

### Gaps
- iberdrola.com (pages and PDFs) returns **403** to curl and WebFetch, so the issuer's own scrip history page and booklet were not used. BORME is the legal primary source instead.
- MEFF (BME derivatives) adjustment notices would give an exchange coefficient per edition, but MEFF's archive is loaded by a form I could not drive with plain requests. Only 2026 notices for other issuers were visible.
- Ex dates are my reading: the first rights-trading day quoted in each notice, which is the day after the stated "last trading date".

