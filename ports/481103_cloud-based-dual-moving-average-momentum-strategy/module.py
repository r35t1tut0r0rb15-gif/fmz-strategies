"""Ichimoku cloud states (9 / 26 / 52, undisplaced), 2-day bars: the close above both spans with Tenkan over Kijun goes long, below both with Tenkan under Kijun goes short; reversing.
Port of FMZ strategy #481103 "Cloud Based Dual Moving Average Momentum Strategy" (Ichimoku Cloud Strategy).

FMZ source id: 481103

Source
    https://www.fmz.com/strategy/481103 (PineScript v5, FMZ last modified 2025-02-08 15:10:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 127-198), Tenkan 9, Kijun 26, span B 52; displacement 26 (plots only)
    close > spanA and close > spanB and tenkan > kijun -> entry Long;  close below both and tenkan < kijun -> entry Short;  the opposite state closes the held side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spans are read at the current bar; the displacement only shifts the plots. The states repeat;
      a repeat on the held side is ignored, and the closes coincide with the reversing entries. REVERSAL
      INTENDED. No sizing code. 2-day bars are blocks of two broker days. FREQ = "2D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku cloud and Tenkan / Kijun states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: two-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_481103_ichimoku_cloud_tk_state_2d_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [9, 20],
    "kijun": [26, 60],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "span_b": 52, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def don(n):
        return (h.rolling(int(n)).max() + lo.rolling(int(n)).min()) / 2

    tk, kj = don(p["tenkan"]), don(p["kijun"])
    a, b = (tk + kj) / 2, don(p["span_b"])
    le = (c > a) & (c > b) & (tk > kj)
    se = (c < a) & (c < b) & (tk < kj)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
