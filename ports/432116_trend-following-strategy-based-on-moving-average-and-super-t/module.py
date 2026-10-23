"""A SuperTrend-style line of the daily bars (low - 1 ATR 50 ratcheting up, high + 1 ATR 50 ratcheting down, trend switched by the close against the other line): the close crossing over the line goes long, crossing under it goes short; broker days, reversing.
Port of FMZ strategy #432116 "Trend Following Strategy Based on Moving Average and Super Trend" (My RK Strategy with Alert (rajukpatel)).

FMZ source id: 432116

Source
    https://www.fmz.com/strategy/432116 (PineScript v5, FMZ last modified 2023-11-14 16:23:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 164-265), res5 "D" (lookahead_on on a 1-day chart); SuperTrend multiplier 1, period 50; tf 1440 (plots only)
    up_trend := c[1] > up_trend[1] ? max(l - 1 atr(50), up_trend[1]) : l - 1 atr(50);  down_trend mirror with hz + 1 atr(50)
    trend := c > down_trend[1] ? 1 : c < up_trend[1] ? -1 : nz(trend[1], 1);  st_line = trend == 1 ? up_trend : down_trend;  crossover(c, st_line) -> entry long, crossunder -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The security() calls ask for res5 "D" on the header's 1-day chart, so o / c / hz / l are the chart
      bar's own values and lookahead_on reads nothing ahead. Volume enters only the volume-weighted EMA
      "ma", which no order uses: the VHMA helper p() sums src5[i] (the close) and never its own argument, and
      the VHMA and the daily candles only feed plots. Volume is not used. ta.atr is the chart's ATR 50 (rma
      of the true range). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR trailing-line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432116_atr50_supertrend_line_cross_daily_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "st_period": [50, 20],
    "st_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"st_period": 50, "st_mult": 1.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    atr = float(p["st_mult"]) * _rma(tr, int(p["st_period"]))
    up_lev = (lo - atr).to_numpy(dtype=float)
    dn_lev = (h + atr).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    st = np.full(m, np.nan)
    ut_p = dt_p = np.nan
    tr_p = 1
    for i in range(m):
        c1 = cv[i - 1] if i else np.nan
        ut = max(up_lev[i], ut_p) if c1 > ut_p else up_lev[i]
        dt = min(dn_lev[i], dt_p) if c1 < dt_p else dn_lev[i]
        t = 1 if cv[i] > dt_p else (-1 if cv[i] < ut_p else tr_p)
        st[i] = ut if t == 1 else dt
        ut_p, dt_p, tr_p = ut, dt, t
    sts = pd.Series(st, index=c.index)
    buy = (c > sts) & (pc <= sts.shift(1))
    sell = (c < sts) & (pc >= sts.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.fillna(False).astype(bool), false, sell.fillna(False).astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
