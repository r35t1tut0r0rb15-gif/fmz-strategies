"""Stochastic RSI 14 (0-100 scale) against thresholds of 0.1 / 0.9 with the Bollinger 20 / 2 bands, broker days, from flat: an average of K and D under 0.1 with the close at the lower band goes long, over 0.9 at the upper band goes short; the average back over 0.2 (under 0.8) closes.
Port of FMZ strategy #489893 "Multi Factor Mean Reversion Strategy A Mean Reversion Trading System Combining Stochastic RSI and Bollinger Bands" (Stochastic RSI & Bollinger Bands Backtest (5 Min)).

FMZ source id: 489893

Source
    https://www.fmz.com/strategy/489893 (PineScript v5, FMZ last modified 2025-04-09 17:05:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 191-252), Stoch RSI 14 / 3 / 3; BB 20 / 2 on security("5", close); levels 0.1 / 0.9, exits 0.2 / 0.8
    stochRSI = (k + d) / 2 of stoch(rsi(close5), 14);  flat and stochRSI < 0.1 and close <= lower -> entry Buy;  flat and > 0.9 and close >= upper -> entry Sell
    long and stochRSI > 0.2 -> close Buy;  short and stochRSI < 0.8 -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * "5" is a lower time frame requested without lookahead: each daily bar gets its last 5-minute close,
      which is the day's close, so the RSI and bands run on daily closes (as #436765). The stochastic is on
      a 0-100 scale while the levels are 0.1 / 0.9 / 0.2 / 0.8, as written: entries need it at its floor or
      ceiling and exits come almost at once. Entries only from flat, with a loop following the position:
      Opposite entries cannot occur. No sizing code. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Stochastic RSI extremes at the Bollinger bands.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489893_stochrsi14_extreme_bb20_2_touch_flat"
FAMILY = "stochastic"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "bbLength": [20, 50],
}
DEFAULT_PARAMS = {"length": 14, "bbLength": 20, "smoothK": 3, "smoothD": 3, "bbStdDev": 2.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    r = _rsi(c, n)
    lo_, hi_ = r.rolling(n).min(), r.rolling(n).max()
    st = 100 * (r - lo_) / (hi_ - lo_).where(hi_ > lo_)
    k = st.rolling(int(p["smoothK"])).mean()
    d = k.rolling(int(p["smoothD"])).mean()
    sr = ((k + d) / 2).to_numpy()
    b = int(p["bbLength"])
    basis = c.rolling(b).mean()
    dev = float(p["bbStdDev"]) * c.rolling(b).std(ddof=0)
    buy = ((c <= basis - dev).to_numpy()) & (sr < 0.1)
    sell = ((c >= basis + dev).to_numpy()) & (sr > 0.9)
    m = len(sr)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend = 0, 0
    for i in range(m):
        if pend != 0:
            pos = 0 if pend == 2 else pend
        pend = 0
        if pos == 0:
            if buy[i]:
                le[i], pend = True, 1
            elif sell[i]:
                se[i], pend = True, -1
        elif pos == 1 and sr[i] > 0.2:
            lx[i], pend = True, 2
        elif pos == -1 and sr[i] < 0.8:
            sx[i], pend = True, 2
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(lx), S(se), S(sx)


def portfolio_kwargs(**params):
    return {}
