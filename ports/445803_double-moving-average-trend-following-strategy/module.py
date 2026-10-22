"""SSL channel flips (SMA 32 of highs and lows), daily bars: the up line crossing over the down line goes long, crossing under goes short; reversing.
Port of FMZ strategy #445803 "Double Moving Average Trend Following Strategy" (Demo - SSL Basic).

FMZ source id: 445803

Source
    https://www.fmz.com/strategy/445803 (PineScript v5, FMZ last modified 2024-03-22 13:56:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 138-200), SSL MA type SMA, length 32; dates 2018-2030 (always true); 100 % of equity, capital 100, commission 0.15
    Hlv = close > sma(high, 32) ? 1 : close < sma(low, 32) ? -1 : Hlv[1];  sslDown = Hlv < 0 ? maHigh : maLow;  sslUp = Hlv < 0 ? maLow : maHigh
    crossover(sslUp, sslDown) -> close Short, entry Long;  crossover(sslDown, sslUp) -> close Long, entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Hlv starts na (int(na)), and na < 0 is false, so the lines start as up = maHigh, down = maLow.
      Each close comes with the opposite entry on the same bar: one reversal. backtest_range is always
      true. REVERSAL INTENDED. The 100 % of equity size is sizing. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SSL channel flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size and capital stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445803_ssl32_flip_reversal"
FAMILY = "ssl_channel"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ssl_len": [32, 10],
}
DEFAULT_PARAMS = {"ssl_len": 32}


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
    n = int(p["ssl_len"])
    mh = h.rolling(n).mean().to_numpy()
    ml = lo.rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    hlv = np.full(m, np.nan)
    v = np.nan
    for i in range(m):
        if cv[i] > mh[i]:
            v = 1.0
        elif cv[i] < ml[i]:
            v = -1.0
        hlv[i] = v
    neg = hlv < 0                                   # na < 0 is false
    dn = pd.Series(np.where(neg, mh, ml), index=c.index)
    up = pd.Series(np.where(neg, ml, mh), index=c.index)
    le = (up > dn) & (up.shift(1) <= dn.shift(1))
    se = (dn > up) & (dn.shift(1) <= up.shift(1))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
