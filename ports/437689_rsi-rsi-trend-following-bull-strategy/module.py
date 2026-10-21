"""RSI dip buys in a down-trending market, broker days, long only: an RSI 14 crossing over 21 with the close under the SMA 200 (or together with a MACD crossing under its signal) buys; an RSI crossing under 86 with
the close above the SMA 200 closes the long, and so does any RSI crossing under 73 (emergency exit).
Port of FMZ strategy #437689 "RSI趋势追踪型多头策略RSI-Trend-Following-Bull-Strategy" (RSI - BULL RUN (Improved)).

FMZ source id: 437689

Source
    https://www.fmz.com/strategy/437689 (PineScript v4, FMZ last modified 2024-01-04 17:48:41).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 118-151), RSI 14; long cross 21, close 86, emergency 73 (on); trend filter SMA 200 (named EMA); MACD 12 / 26 / 9
    longCondition = crossover(rsi, 21) and close < sma 200 or crossunder(macd, signal) and crossover(rsi, 21);  close Long on crossunder(rsi, 86) and close > sma 200;  close Long on crossunder(rsi, 73)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "EMA trend filter" is an SMA as coded, and the long needs the close UNDER it (trendDown), as
      written. The emergency exit fires on every crossing under 73. A same-side entry while long is
      ignored. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI levels, SMA side, MACD crossing.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_437689_rsi_dip_buy_emergency_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_long": [21.0, 30.0],
    "ema_length": [200, 100],
}
DEFAULT_PARAMS = {"rsi_long": 21.0, "ema_length": 200, "rsi_close": 86.0, "rsi_emergency": 73.0}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, 14)
    r1 = r.shift(1)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    tr = c.rolling(int(p["ema_length"])).mean()
    rl, rc, re_ = float(p["rsi_long"]), float(p["rsi_close"]), float(p["rsi_emergency"])
    x_l = (r > rl) & (r1 <= rl)
    lc = (x_l & (c < tr)) | ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & x_l)
    xc = ((r < rc) & (r1 >= rc) & (c > tr)) | ((r < re_) & (r1 >= re_))
    false = pd.Series(False, index=bars_df.index)
    return lc, xc, false, false.copy()


def portfolio_kwargs(**params):
    return {}
