"""Ichimoku cloud breakouts on the displaced cloud, broker days: the close crossing over the top of the 52-bar-displaced cloud goes long; the close crossing under the bottom edge goes short (reversing). Tenkan 18, Kijun 60,
Senkou B 30.
Port of FMZ strategy #436652 "Ichimoku Balance Line Strategy" (Cloud Breakout (Ichimoku)).

FMZ source id: 436652

Source
    https://www.fmz.com/strategy/436652 (PineScript v3, FMZ last modified 2023-12-26 16:13:42).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 129-228), Tenkan 18, Kijun 60, Senkou B 30, displacement 52
    TS = donchian(18), KS = donchian(60), SpanA = avg(TS, KS), SpanB = donchian(30), donchian(n) = avg(lowest(n), highest(n));  SpanAA = SpanA[52], SpanBB = SpanB[52];  SpanA_Top = SpanAA >= SpanBB, SpanB_Top = SpanBB >= SpanAA
    Long_Breakout = (SpanA_Top and crossover(close, SpanAA)) or (SpanB_Top and crossover(close, SpanBB));  Short_Breakout = (SpanA_Top and crossunder(close, SpanBB)) or (SpanB_Top and crossunder(close, SpanAA))
    entry long when Long_Breakout;  entry short when Short_Breakout

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cloud values are read 52 bars back (the cloud drawn at the bar). The other conditions (kumo
      twist, chikou, tenkan crossings) are computed but place no orders. The test window is always
      true. REVERSAL INTENDED. The percent-of-equity size is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud breakout.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429159 (2 members, best partner #429159, Jaccard 0.767); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436652_ichimoku_cloud_breakout"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [18, 9],
    "span_offset": [52, 26],
}
DEFAULT_PARAMS = {"tenkan": 18, "kijun": 60, "senkou_b": 30, "span_offset": 52}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def donchian(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    ts, ks = donchian(p["tenkan"]), donchian(p["kijun"])
    k = int(p["span_offset"])
    span_aa = ((ts + ks) / 2).shift(k)
    span_bb = donchian(p["senkou_b"]).shift(k)
    a_top, b_top = span_aa >= span_bb, span_bb >= span_aa

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    long_b = (a_top & xo(c, span_aa)) | (b_top & xo(c, span_bb))
    short_b = (a_top & xu(c, span_bb)) | (b_top & xu(c, span_aa))
    false = pd.Series(False, index=bars_df.index)
    return long_b.fillna(False).astype(bool), false, short_b.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
