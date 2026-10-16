"""Smoothed Heikin Ashi, 2-day bars, long only: Heikin Ashi candles built from EMA 65 of the open, high,
low and close; three bullish candles with rising closes go long, three bearish ones with falling closes
close it (signals alternate).
Port of FMZ strategy #428608 "Heikin Ashi Smoothed Buy and Sell Strategy" (Abdoli's Rev.4).

FMZ source id: 428608

Source
    https://www.fmz.com/strategy/428608 (PineScript v4, FMZ last modified 2023-10-07 15:01:06).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 126-161), EMA 65
    haClose = mean of the four EMAs; haOpen := na(haOpen[1]) ? (maOpen[1] + maClose[1]) / 2 : (haOpen[1] + haClose[1]) / 2
    Buy = three positive bodies and haClose rising twice; Sell mirrors
    Buy_final = Buy and last signal not a buy; Sell_final = Sell and last signal not a sell
    Buy_final -> entry long; Sell_final -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * last_signal is not var but carries itself through [1] (as var). Long only.
    * 2-day bars are blocks of broker days counted from 1970-01-01 (as worker A's 2-day ports),
      stamped with the session start. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA length only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428608_smoothed_heikin_ashi_long"
FAMILY = "heikin_ashi"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_period": [65, 30, 45, 100],
}
DEFAULT_PARAMS = {"ma_period": 65}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["ma_period"])
    mo, mh, ml, mc = (bars_df[k].ewm(span=n, adjust=False).mean().to_numpy() for k in ("open", "high", "low", "close"))
    hc = (mo + mh + ml + mc) / 4
    m = len(hc)
    ho = np.full(m, np.nan)
    for i in range(1, m):
        ho[i] = (mo[i - 1] + mc[i - 1]) / 2 if np.isnan(ho[i - 1]) else (ho[i - 1] + hc[i - 1]) / 2
    b = hc - ho
    tgt = np.zeros(m, dtype=np.int8)
    last, pos = 0, 0
    for i in range(2, m):
        buy = b[i] > 0 and b[i - 1] > 0 and b[i - 2] > 0 and hc[i] > hc[i - 1] and hc[i - 1] > hc[i - 2]
        sell = b[i] < 0 and b[i - 1] < 0 and b[i - 2] < 0 and hc[i] < hc[i - 1] and hc[i - 1] < hc[i - 2]
        bf = buy and last in (0, -1)
        sf = sell and last in (0, 1)
        last = 1 if bf else (-1 if sf else last)
        if bf:
            pos = 1
        elif sf:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
