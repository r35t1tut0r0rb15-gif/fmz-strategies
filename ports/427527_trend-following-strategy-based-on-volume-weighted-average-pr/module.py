"""Ichimoku-style lead lines built from rolling VWAPs (slow 9 / 26 and fast 5 / 13 periods), a Bollinger 20 / 2 band of their average and the time-segmented volume (TSV 13 with EMA 7), broker days, long only: both lead lines rising with a positive TSV above its EMA and the close above the upper band goes long; both lead lines falling closes.
Port of FMZ strategy #427527 "Trend Following Strategy Based on Volume weighted Average Price and Volatility" (HYE Trend Hunter [Strategy]).

FMZ source id: 427527

Source
    https://www.fmz.com/strategy/427527 (PineScript v4, FMZ last modified 2023-09-21 21:32:40).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-289), VWAP lines 9 / 26 (slow), 5 / 13 (fast); BB 20, 2; TSV 13, EMA 7; pyramiding 0
    vwap_n = sum(hlc3 x volume, n) / sum(volume, n);  tenkan / kijun = mid of the lowest / highest vwap_n over n;  leadLine = avg(tenkan, kijun)  (slow and fast)
    fast and slow lead lines rising and tsv > 0 and tsv > ema(tsv, 7) and close > upper BB(avg(fast, slow), 20, 2) -> entry BUY;  both falling -> close BUY

Interpretation choices (Pine rules in SURVEY_README.md)
    * The fast Kijun line reuses the slow typical price (the same hlc3, as written). TSV is the 13-bar sum
      of volume x the close change. The author's date range is not used (inDateRange = true). Long only.
      The 100 % of equity size and commission are sizing / costs. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, VWAP lead lines with a volume-flow and band breakout filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, capital 1000, commission 0.025 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the rolling VWAPs and the TSV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427527_vwap_ichimoku_lead_lines_bb_tsv_long"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 10],
    "tsv_length": [13, 26],
}
DEFAULT_PARAMS = {"bb_length": 20, "tsv_length": 13, "bb_mult": 2.0, "tsv_ema": 7, "slow_t": 9, "slow_k": 26,
                  "fast_t": 5, "fast_k": 13}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    tpv = (h + lo + c) / 3 * v
    vw = lambda n: tpv.rolling(n).sum() / v.rolling(n).sum()
    mid = lambda x, n: (x.rolling(n).min() + x.rolling(n).max()) / 2
    st, sk, ft, fk = (int(p[k]) for k in ("slow_t", "slow_k", "fast_t", "fast_k"))
    slow = (mid(vw(st), st) + mid(vw(sk), sk)) / 2
    fast = (mid(vw(ft), ft) + mid(vw(fk), fk)) / 2
    bbl = (fast + slow) / 2
    n = int(p["bb_length"])
    upper = bbl.rolling(n).mean() + float(p["bb_mult"]) * bbl.rolling(n).std(ddof=0)
    tsv = (v * c.diff()).fillna(0.0).rolling(int(p["tsv_length"])).sum()
    tsv_e = tsv.ewm(span=int(p["tsv_ema"]), adjust=False).mean()
    le = (fast > fast.shift(1)) & (slow > slow.shift(1)) & (tsv > 0) & (tsv > tsv_e) & (c > upper)
    lx = (fast < fast.shift(1)) & (slow < slow.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
