"""Broker days: OBV crossing over its EMA 13 while the previous bar's CCI 20 was at or above 0 goes long; OBV crossing under its EMA while the previous CCI was below 0 goes short; reversing.
Port of FMZ strategy #442364 "基于OBV和CCI指标的趋势追踪策略OBV-and-CCI-Indicators-Based-Trend-Following-Strategy" (SB_CCI coded OBV Strategy (SudeepBisht)).

FMZ source id: 442364

Source
    https://www.fmz.com/strategy/442364 (PineScript v3, FMZ last modified 2024-02-21 14:05:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 157-181), CCI 20, threshold 0; EMA 13 of OBV
    o = obv(close);  c = cci(close, 20);  chk = c >= 0 ? 1 : 0;  ema_line = ema(o, 13)
    crossover(o, ema_line) and chk[1] == 1 -> entry RsiLE;  crossunder(o, ema_line) and chk[1] == 0 -> entry RsiSE

Interpretation choices (Pine rules in SURVEY_README.md)
    * CCI is Pine's (mean absolute deviation, 0.015). chk[1] before the CCI exists is 0 (red), so early
      short signals pass, as written. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OBV / EMA crossings coded by the CCI sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442364_obv_ema13_cross_cci_coded_reversal"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_len": [20, 14],
    "ema_len": [13, 26],
}
DEFAULT_PARAMS = {"cci_len": 20, "threshold": 0.0, "ema_len": 13}


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


def _cci(x, n):
    sma = x.rolling(n).mean()
    mad = pd.Series(np.nan, index=x.index)
    if len(x) >= n:
        win = np.lib.stride_tricks.sliding_window_view(x.to_numpy(dtype=float), n)
        mad.iloc[n - 1:] = np.abs(win - win.mean(axis=1, keepdims=True)).mean(axis=1)
    return (x - sma) / (0.015 * mad).where(mad != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    d = c.diff()
    obv = pd.Series(np.where(d > 0, v, np.where(d < 0, -v, 0.0)), index=c.index).cumsum()
    chk = (_cci(c, int(p["cci_len"])) >= float(p["threshold"])).shift(1, fill_value=False)
    e = obv.ewm(span=int(p["ema_len"]), adjust=False).mean()
    up = (obv > e) & (obv.shift(1) <= e.shift(1)) & chk
    dn = (obv < e) & (obv.shift(1) >= e.shift(1)) & ~chk
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
