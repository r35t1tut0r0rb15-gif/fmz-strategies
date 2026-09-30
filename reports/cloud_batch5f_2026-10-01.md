# Cloud batch 5f: inventory, coarse-bar stops, corporate-action inputs

- Repository: `r35t1tut0r0rb15-gif/fmz-strategies` (a GitHub fork)
- Branch: `cloud-batch5f-2026-10-01`, cut from `master` @ `7853bb2`
- Work done: 2026-09-30 (UTC). Every "checked" date below is 2026-09-30.
- Scope: read-only. No backtests, no mining, no strategy changes, nothing deleted. The only files added are this report and `reports/cloud_coarse_bar_stops_2026-10-01.csv`.

---

## Task 1: Where is the converted FMZ output?

**Answer: no converted FMZ strategies exist in any branch, folder, commit, tag or pull request this session can see.** No branch named `survey` exists. Every branch holds only the original FMZ source files (Markdown pages with embedded PineScript, JavaScript, Python, MyLanguage or C++ source). None holds converted code: no `.py`/`.js` files and no output folders.

### Branches on GitHub (`git ls-remote origin` and the GitHub branches API, checked 2026-09-30)

| Branch | Newest commit | Date of newest commit | Commits | Files | What it holds beyond `master` |
|---|---|---|---|---|---|
| `master` | `7853bb2bf262c4567ac238d3552d97f0e50cb801` | 2025-04-30 11:10:28 +0800 ("update", author "root") | 50 | 5,807 | n/a: 5,806 FMZ strategy `.md` files + `README.md`, all at the repo root, no subfolders |
| `corp-actions-research` | `10ed914139a789bd7d240e01e8cdf8b9efa8a89f` | 2026-09-28 08:19:00 +0000 | 51 | 5,808 | 1 file: `batch5d_corp_actions_sourcing_2026-09-28.md` (parent = `7853bb2`) |
| `corp-actions-sourcing` | `7f22a38dae8435416509198e9cf5cfcf8a751eb7` | 2026-09-29 00:05:33 +0000 | 65 | 5,809 | 2 files: `sourcing/batch5d_corp_actions_sourcing_2026-09-29.md`, `sourcing/adjustment_factors_proposed.csv` (15 commits on top of `7853bb2`) |
| `cloud-batch5f-2026-10-01` (this branch) | this commit | 2026-09-30 | 51 | 5,809 | this report + CSV |

Other facts:
- The local clone also had a tracking ref `origin/claude/clever-ritchie-aiirbz` pointing at `7853bb2` (same as `master`). That branch is **not** on GitHub (ls-remote and the branches API list only the three branches above).
- Tags: none. Stashes: none. Open or closed pull requests: none.
- Other repositories reachable from this session: none (`list_repos` returns only this fork).
- Oldest commit on `master`: `d95749b`, 2017-01-26 (author "botvs"). Newest: `7853bb2`, 2025-04-30.

### What the 5,806 strategy files are (all on `master`, unchanged on every other branch)

| Source language (from the `> Source (…)` header) | Files |
|---|---|
| PineScript | 5,283 |
| javascript | 362 |
| python | 131 |
| MyLanguage | 27 |
| cpp | 3 |
| **Total** | **5,806** |

Each file carries an FMZ strategy id in its `> Detail` link (`https://www.fmz.com/strategy/<id>`). Nine ids appear in two files each (18 files): 182185, 188435, 191582, 193609, 195226, 200131, 322357, 397260, 405725.

---

## Task 2: Coarse-bar stop strategies

### Population used, and why

The request says "among the converted FMZ strategies", but no converted set exists (Task 1). **I ran the count on the 5,806 original FMZ source files instead, as a proxy.** Whether this proxy is acceptable is decision 1 below.

### Method

- **Bar size** is the `period:` value in the FMZ `/*backtest … */` config block embedded in each file's source. "Longer than 60 minutes" means `period` > 60 min. The strategy's name was not used: for example, "4小时CCI反转策略 4-Hour-CCI-Reversal-Strategy" (id 429145) has `period: 3h`. The CSV also carries `basePeriod`, the finer bar FMZ uses to simulate fills.
- **Stop detection** runs on the source code only, with comments and the backtest block removed:
  - **confirmed**: a PineScript `strategy.exit(...)` call with `stop=`/`loss=` (SL), `limit=`/`profit=` (TP), or `trail_points=`/`trail_offset=`/`trail_price=` (trailing). `stop=` on `strategy.entry`/`strategy.order` is a stop *entry*, so it was not counted.
  - **probable**: no qualifying `strategy.exit` call, but stop/target identifiers appear in the code (`stop_loss`, `stoploss`, `止损`, `take_profit`, `止盈`, `trailing stop`, `移动止损`, `sl_*`, `tp_*`, and similar).
- The scan was a static text scan. Nothing was executed.

### Result

**1,352 files: 1,015 confirmed + 337 probable**, covering 1,351 distinct strategy ids (id 405725 appears in two files, both 1d SL+TP). All 1,015 confirmed rows are PineScript. The 337 probable rows are 327 PineScript + 10 JavaScript.

| Bar size | Confirmed | Probable | Total |
|---|---|---|---|
| 2h | 116 | 39 | 155 |
| 3h | 68 | 15 | 83 |
| 4h | 82 | 23 | 105 |
| 5h | 3 | 2 | 5 |
| 6h | 3 | 1 | 4 |
| 7h | 1 | 0 | 1 |
| 8h | 1 | 0 | 1 |
| 12h | 6 | 0 | 6 |
| 15h | 1 | 0 | 1 |
| 1d | 678 | 245 | 923 |
| 2d | 43 | 8 | 51 |
| 3d | 6 | 3 | 9 |
| 4d | 5 | 0 | 5 |
| 5d | 1 | 1 | 2 |
| 6d | 1 | 0 | 1 |
| **Total** | **1,015** | **337** | **1,352** |

Stop type across all 1,352 rows (confirmed only in brackets): SL+TP 768 (659), SL 288 (186), TP 110 (61), SL+TP+trailing 77 (51), trailing 56 (27), SL+trailing 43 (22), TP+trailing 10 (9).

`basePeriod` equals `period` in 476 of the 1,352 rows. In those rows the backtester has no finer bars to simulate fills with.

For context, all 5,806 files break down like this: 2,638 have stop logic detected, of which 1,352 are coarse (> 60 min), 1,191 are ≤ 60 min and 95 have no bar size. The other 3,168 have no stop logic detected.

CSV: `reports/cloud_coarse_bar_stops_2026-10-01.csv` (1,352 rows). Columns: `strategy_id, bar_size, stop_type, detection (confirmed|probable), language, base_period, file`.

### Could not classify

1. **95 files with stop logic but no bar size.** Their source has no `/*backtest*/` block, so there is no `period` to read (PineScript 40, JavaScript 34, Python 16, MyLanguage 5). I did not guess a bar size from names or descriptions. Ids: 64, 179, 358, 629, 2169, 3648, 8474, 9929, 13594, 13597, 30861, 91704, 113144, 113796, 113979, 113986, 117768, 119038, 121081, 126968, 127101, 129078, 157366, 157372, 182656, 187874, 192353, 194150, 194224, 195226, 201963, 203272, 211262, 227783, 237682, 261634, 286091, 301145, 301404, 313041, 319427, 319429, 320782, 322060, 322094, 322284, 330440, 340779, 340820, 343745, 345080, 348791, 361786, 362031, 362169, 375951, 376193, 376259, 376260, 376261, 376263, 376304, 381042, 392636, 395962, 396182, 400134, 410114, 422794, 427369, 427392, 428756, 429401, 429950, 430013, 432889, 433078, 434679, 434680, 436597, 442652, 446468, 446552, 446558, 446560, 446984, 452822, 457811, 458034, 458133, 458134, 483063, 483075, 491891. (Id 195226 is two files, so 94 ids cover 95 files.)
2. **Two files with a unit-less `period`**: id 61867 (`period: 1440`) and id 40155 (`period: 15`). The unit is not stated. Neither has stop logic detected, so neither affects the count.
3. **Known limits of the method (not quantified):**
   - *False negatives*: a strategy that exits with `strategy.close()` on a price condition, under variable names the keyword list doesn't match, is missed. Non-Pine languages only get the keyword test.
   - *False positives in the "probable" tier*: a spot check of 12 random probable rows found display-only or unused inputs. Examples: id 442080, `input(title='Show Stop Loss Line')`; id 478707, stop and target colour inputs; id 426809, a supertrend line named `longStop`. **The 337 probable rows need a manual check before use.**
4. `README.md` is not a strategy and was excluded.

---

## Task 3: Corporate-action inputs (primary sources only)

Rules followed: verbatim quotes, URL and date checked for each value. No value was computed or inferred from price data. Where a copy is archived, the archive URL is given, and the document's own original URL is also listed.

### (a) PFE 2020-11-17 Upjohn/Viatris spinoff: Form 8937 basis split. **SOURCED: 94.8% Pfizer / 5.2% Viatris**

**Step 1: the Viatris-hosted URL you gave.**
URL: https://investor.viatris.com/static-files/17c6dcf3-d300-493a-b1c3-e990137af3d6 (checked 2026-09-30).
- Plain `curl` (default user agent) got HTTP 200: `application/pdf`, `content-disposition: inline; filename="Form 8937_VTRS.pdf"`, 127,136 bytes, SHA-256 `098852523ce9398d714826fa30d65fb178a566dacfed7d898abc99b80bfcd070`. A browser-style user agent got HTTP 403.
- **This document is not the Pfizer 8937.** It is **Viatris Inc.'s own Form 8937 for the Mylan side of the Combination**, and it gives no Pfizer/Viatris split. Verbatim:
  > "Viatris Inc. 83-4364296 … November 16, 2020 Stock 92556V 106; N59465 109 VTRS"
  >
  > "On November 16, 2020 Mylan N.V. ("Mylan") effected a strategic business combination transaction with Viatris Inc. ("Viatris"), pursuant to which holders of Mylan ordinary shares received, in exchange for their Mylan ordinary shares, shares of Viatris common stock in a taxable transaction (the "Combination")."
  >
  > "Viatris intends to take the position in all applicable tax filings that the fair market value of each share of Viatris commo stock and each Mylan ordinary share, each at the time of the Combination, was equal to $15.66, which was the per share closing price Viatris as displayed under the heading "Last Price" on the Bloomberg page for "VTRSV" for the date of the Combination (November 16, 2020)."

  (Typos such as "commo stock" are in the original.)

**Step 2: Pfizer's own Form 8937 (issuer document, archived copy).**
- Original URL (now HTTP 404): https://s21.q4cdn.com/317678438/files/doc_news/2020/08/Distribution-Tax-Basis-Information.pdf
- Archived copy read: https://web.archive.org/web/20240616120847/https://s21.q4cdn.com/317678438/files/doc_news/2020/08/Distribution-Tax-Basis-Information.pdf (checked 2026-09-30). HTTP 200, `application/pdf`, 5 pages, 414,250 bytes, SHA-256 `e7540bf845937462ebaf0afb5155b377a28a6501b69e14e10460c651f8719842`. PDF title "Form 8937 (Rev. December 2017)", created 2020-11-30.
- Form fields, page 1: Issuer "Pfizer Inc.", EIN "13-5315170", Date of action "November 16, 2020", Classification "Common Stock", CUSIP "717081103", Ticker "NYSE: PFE".
- Verbatim, Line 16 (the split):
  > "One method to determine the fair market value is to use the closing prices of the Pfizer and Viatris common stock on the Distribution Date. The adjusted closing price of each share of Pfizer common stock on the Distribution Date was $35.3869, which was the per share closing price as displayed under the heading "Last Price" on the Bloomberg page for the ticker "PFE." The closing price for each share of Viatris common stock on the Nasdaq's "when-issued" market on the Distribution Date was $15.66, which was the per share closing price as displayed under the heading "Last Price" on the Bloomberg page for the ticker "VTRSV." Using these prices for purposes of determining fair market value, and the distribution ratio of approximately 0.124079 of a share of Viatris common stock for each share of Pfizer common stock, a Pfizer shareholder's pre-distribution tax basis in each Pfizer share should be allocated 94.8% to the Pfizer share and 5.2% to the Viatris share (including any Viatris fractional share) received with respect to the Pfizer share."
- Verbatim, footnote 2:
  > "The unadjusted closing price of Pfizer common stock on the Distribution Date was $37.33. The adjusted closing price of Pfizer common stock on the Distribution Date was calculated by subtracting the value of Viatris common stock for each share of Pfizer common stock (i.e., the product of 0.124079 and $15.66) from the unadjusted closing price of Pfizer common stock on that date."
- Verbatim, Line 14:
  > "On November 16, 2020 (the "Distribution Date"), Pfizer Inc. ("Pfizer") distributed 100% of the outstanding shares of common stock of Viatris Inc., formerly known as Upjohn Inc. ("Viatris"), pro rata to Pfizer shareholders of record as of the close of business on November 13, 2020"

**Ex-date cross-check (exchange data).** NYSE Corporate Actions API: https://www.nyse.com/api/nyseservice/v1/corpax/?action_date__gte=2020-11-10&action_date__lte=2020-11-20&page=1&page_size=100 (checked 2026-09-30). This is the data behind https://www.nyse.com/trade/corporate-actions.
> `{"action_date": "2020-11-17", "action_status": "Effective before the Open", "action_type": "Suspend - \"Ex-Distribution\" Market", "issue_symbol": "PFE WI", "issuer_name": "Pfizer Inc"}`

My reading: the NYSE ex-distribution market closed before the open on 2020-11-17, which fits a regular-way ex date of 2020-11-17.

Note: the 8937 split is measured at Distribution Date (2020-11-16) closes, including a when-issued VTRSV price, not at a cum/ex pair. This is the same point as batch 5d's decision 2.

### (b) BABA special dividends US$0.66/ADS and US$0.95/ADS

**NYSE ex-dates: SOURCED (OCC clearing notices, archived copies).** OCC's live site returned a Cloudflare "Just a moment…" challenge (HTTP 403). I did not try to bypass it. I read the archived PDFs instead.

- **2024: OCC Information Memo #54634**, dated May 24, 2024.
  Original: https://infomemo.theocc.com/infomemos?number=54634
  Read at: https://web.archive.org/web/20240613142401/https://infomemo.theocc.com/infomemos?number=54634 (checked 2026-09-30). PDF, SHA-256 `dd01b2b20af7e5aa079ae74b0a80c77b517fdf5736d35db9d0e17c785b7da4b9`.
  > "Alibaba Group Holding Limited (BABA) has announced a Special Cash Dividend of approximately $0.66, less fees, if any, per BABA American Depositary Share. The record date is June 13, 2024; payable date is July 12, 2024. The ex-distribution date for this distribution will be June 13, 2024."
  >
  > "Effective Date:June 13, 2024 … Deliverable Per Contract:1) 100 Alibaba Group Holding Limited (BABA) American Depositary Shares 2) Approximately $66.00 Cash (approximately $0.66 x 100), less fees, if any CUSIP:01609W102"
- **2025: OCC Information Memo #56574**, dated May 19, 2025.
  Original: https://infomemo.theocc.com/infomemos?number=56574
  Read at: https://web.archive.org/web/20250730155704/https://infomemo.theocc.com/infomemos?number=56574 (checked 2026-09-30). PDF, SHA-256 `a32a98438749b23a9ee70e38a8ec4b2485870dfd0fb7cf058613eb1c27fdb4cd`.
  > "Alibaba Group Holding Limited (BABA) has announced a Special Cash Dividend of approximately $0.95, less fees, if any, per BABA American Depositary Share. The record date is June 12, 2025; payable date is July 10, 2025. The ex-distribution date for this distribution will be June 12, 2025."
- Issuer confirmation of the amounts and the ADS record dates is already in batch 5d, from the Alibaba 6-Ks on SEC EDGAR. For example, FY2024 (https://www.sec.gov/Archives/edgar/data/1577552/000110465924061145/tm2414429d1_ex99-1.htm): "a one-time extraordinary cash dividend … in the amount of US$0.0825 per ordinary share or US$0.66 per ADS … as of the close of business on June 13, 2024, Hong Kong Time and New York Time, respectively."
- Note: the OCC memos give ADS payable dates of **July 12, 2024** and **July 10, 2025**. The HKEX forms in batch 5d give 03 July for the ordinary shares.
- Search snippets also named later OCC memos #54725 and #54868 (2024) and #56699, #56734 and #56856 (2025). **I did not read them** (no archived copy of #54725; the archive lookup for #56699 timed out; the others were not attempted), so nothing is taken from them.

**NYSE closes on the last trading day before each ex-date (2024-06-12 and 2025-06-11): NOT SOURCED from a primary source.**
- SEC EDGAR full-text search (efts.sec.gov, checked 2026-09-30) found no filing that states BABA's close on 2024-06-12 or 2025-06-11. I searched with "Alibaba"/"BABA" + the date, with and without "closing price", across 424B2/FWP/424B3 and all forms. An Alibaba 6-K of 2025-06-13 mentions June 11, 2025, but only for Hong Kong next-day disclosure returns, which give no NYSE price.
- OCC memos give no closing prices. The NYSE Corporate Actions feed has no cash-dividend records.
- **Candidate values, not accepted:** NYSE's quote API behind https://www.nyse.com/quote/XNYS:BABA, https://www.nyse.com/api/nyseservice/v1/quotes?symbol=BABA (checked 2026-09-30), returns a `quoteHistory` series. It shows `2024/06/12 … "close": "78.04"` and `2025/06/11 … "close": "120.33"`. **I have not accepted these as sourced**, because:
  1. It is a quote-history feed, not an exchange notice, and it doesn't say whether "close" is the NYSE official closing price.
  2. The same feed is **back-adjusted for at least some corporate actions**. GE's history in it shows six-decimal prices before its spinoffs (e.g. `2024/04/01 "close": "139.855036"`), so the feed's values are not always as-traded prices.

  Accepting or rejecting these values is decision 3.

### (c) GE, last trading day before the Wabtec distribution (ex 2019-02-26)

**Ex-date: SOURCED (exchange data).** NYSE Corporate Actions API, https://www.nyse.com/api/nyseservice/v1/corpax/?action_date__gte=2019-02-01&action_date__lte=2019-03-05&page=1&page_size=100 (checked 2026-09-30):
> `{"action_date": "2019-02-26", "action_status": "Effective before the Open", "action_type": "Suspend - \"Ex-Distribution\" Market", "issue_symbol": "GE WI", "issuer_name": "General Electric Company", "updated_at": "2019-02-25T09:01:09.504325-05:00"}`
>
> `{"action_date": "2019-02-14", "action_status": "Effective before the Open", "action_type": "Admit - \"Ex-Distribution\" Market", "issue_symbol": "GE WI", "issuer_name": "General Electric Company"}`

So the last trading day before the ex date is 2019-02-25 (my reading of these records together with GE's "hold through February 25th close of trade", quoted in batch 5d).

**Close on 2019-02-25: $10.82, SOURCED from an SEC filing, with a caveat.**
UBS AG Final Terms Supplement (Rule 424(b)(2)) for Trigger Phoenix Autocallable Optimization Securities linked to GE, filed 2019-02-25. URL: https://www.sec.gov/Archives/edgar/data/1114446/000111444619000573/tc5052366f_1fwp.htm (checked 2026-09-30).
> "Trade Date February 25, 2019"
>
> "Initial Price $10.82, which is the closing price of the underlying asset on the trade date, as determined by the calculation agent"
>
> "Closing Price On any trading day, the last reported sale price (or, in the case of NASDAQ, the official closing price) of the underlying asset during the principal trading session on the principal national securities exchange on which it is listed for trading, as determined by the calculation agent."
>
> "UBS has not undertaken an independent review or due diligence of any publicly available information obtained from Bloomberg. General Electric's closing price on February 25, 2019 was $10.82."

Caveats:
- This is an SEC filing, but the filer is UBS, not GE, and UBS says its price data comes from Bloomberg.
- The $10.82 is on the pre-2021 share basis, before the 1:8 reverse split.
- GE's own 2019 proxy (below) states no share price for that date.

**Related issuer figure (not the requested close).** GE DEF 14A filed 2019-03-18, https://www.sec.gov/Archives/edgar/data/40545/000120677419000903/ge3496121-def14a.htm (checked 2026-09-30):
> "Amounts presented in the tables above do not reflect an adjustment that was made by the Compensation Committee to the equity awards for the named executives (other than Mr. Culp's PSU grant) as a result of the merger of GE Transportation and Wabtec and the subsequent spin-off of Wabtec shares to GE shareowners on February 25, 2019. This anti-dilutive adjustment was made to preserve the value of the awards following the spin-off. Subsequent to the spin-off, all amounts under "Number Outstanding" and "Portion Exercisable" were subject to an adjustment by multiplying the number shown by 1.04038. Amounts under the "Exercise Price" column were subject to an adjustment by multiplying the number shown by 0.96118."

This is an issuer-stated anti-dilution ratio for equity awards. Its method is not disclosed. See decision 5.

### Access log (checked 2026-09-30)

| Host | Result |
|---|---|
| investor.viatris.com | 200 with default curl UA; 403 with a browser UA |
| s21.q4cdn.com (Pfizer 8937 original) | 404 |
| investors.pfizer.com, www.pfizer.com | 403 |
| web.archive.org over **https** | 200 (Pfizer 8937, OCC #54634, OCC #56574); CDX lookups sometimes reset and succeeded on retry. Plain **http** was refused by the session proxy (403) |
| archive.org availability API | 429 |
| infomemo.theocc.com, www.theocc.com | Cloudflare challenge (403), **not bypassed** |
| www.nyse.com (corporate-actions and quotes APIs) | 200 |
| www.sec.gov, efts.sec.gov | 200 |
| depositaryreceipts.citi.com | 200 (home page only; no BABA notice found) |

---

## For the project chat

### Finished
- **Task 1:** inventory done. There is **no converted FMZ output anywhere**: no `survey` branch, and nothing converted on `master`, `corp-actions-research`, `corp-actions-sourcing`, any tag, PR or other repo. `master` @ `7853bb2` (2025-04-30) holds 5,806 original FMZ source files.
- **Task 2 (on the proxy population):** 1,352 coarse-bar stop files (1,015 confirmed + 337 probable), 923 of them daily. CSV written. 95 files could not be classified (no bar size).
- **Task 3(a):** PFE 8937 split **94.8% / 5.2% sourced**, verbatim, from Pfizer's own Form 8937 (archived copy). The Viatris-hosted file turned out to be Viatris's own 8937 for the Mylan side, with no split. NYSE data confirms the PFE ex date 2020-11-17.
- **Task 3(b) ex-dates:** BABA NYSE ex-dates **2024-06-13** and **2025-06-12** sourced from OCC memos #54634 and #56574 (archived copies).
- **Task 3(c):** GE ex date 2019-02-26 confirmed by NYSE data. GE close on 2019-02-25 = **$10.82** from a UBS 424(b)(2) SEC filing (Bloomberg-derived; decision 4).

### Failed
- **Task 3(b) closes:** no primary source found for BABA's NYSE close on **2024-06-12** or **2025-06-11**. The NYSE quote feed has values (78.04, 120.33), but I did not accept them (decision 3).
- **Task 2 as literally asked:** impossible, because no converted strategies exist.

### Decisions owed
1. **Task 2 population.** Accept the FMZ-source proxy (1,352), or point to where the conversion output actually lives. If an earlier chat reported converting strategies, that work was never pushed to this fork. **Recommend:** confirm where it lives before relying on these counts for converted code.
2. **"Probable" tier (337 rows).** Keyword-only detection includes display-only inputs. **Recommend:** use the 1,015 confirmed rows now, and review the probable rows by hand (or with a stricter parser) before use.
3. **BABA cum closes.** Accept the nyse.com quote-history values (78.04 / 120.33) as exchange-sourced, or keep them unsourceable? **Recommend: do not accept.** The feed is back-adjusted for some actions and doesn't document its close. Use batch 5d decision 4 instead: the loader takes the cum close from its own unadjusted feed, tagged `computed-from-feed`.
4. **GE $10.82.** It is an SEC filing, but by a third party (UBS) citing Bloomberg, and it is the "last reported sale price", not explicitly the NYSE official close. **Recommend:** accept it, tagged `sec-filing-third-party`.
5. **GE proxy ratios 1.04038 / 0.96118.** These are issuer-stated equity-award adjustments for the Wabtec spinoff. **Recommend:** record them as an issuer cross-check only, not as the price factor, because GE doesn't state how they were derived.
6. **Branch.** This work is on `cloud-batch5f-2026-10-01`, as the brief asked. It was not put on the session's default `claude/clever-ritchie-aiirbz` branch, which doesn't exist on GitHub. Say if you want it moved or merged anywhere.
