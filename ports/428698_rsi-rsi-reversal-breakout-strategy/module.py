"""RSI(2) dip buyer above the EMA 200, long only, 2-day bars: with the close at or above the EMA, RSI 2 at
or under 25 buys; the long is sold when a close reaches the high of two bars earlier (also only above the EMA).
Port of FMZ strategy #428698 "RSI反转突破策略RSI-Reversal-Breakout-Strategy".

FMZ source id: 428698

Source
    https://www.fmz.com/strategy/428698 (PineScript v4, FMZ last modified 2023-10-08 14:16:57).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 202-251), RSI 2 <= 25, EMA 200, exit close >= high[2]
    if close >= ema(close,200):
        not comprado and rsi(close,2) <= 25 -> comprado := true, strategy.order buy
        close >= high[2] and comprado -> comprado := false, strategy.order sell (same quantity)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both rules sit inside `close >= EMA 200`: below the EMA neither a buy nor a sell happens (as
      written; a long can be held through a fall below the EMA).
    * A buy and a sell on the same bar (the sell rule sees comprado already set) send two opposite
      orders that fill together at the next open: no position results, so the port emits nothing and
      stays flat (as written, net).
    * The SMA 200, the profit counter and the day counter are drawn or counted only. The date-range
      inputs are the author's backtest window (inDateRange is true): dropped.
    * Long only. Multi-day bars are blocks of 2 broker days (17:00 America/New_York) counted from
      1970-01-01, each stamped with its first minute. FREQ = "2D" from the backtest header (period 2d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI level and price comparisons only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy() line and the quantity input stored.
    5 ranges declared: GRID below (6 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428698_rsi2_dip_above_ema200"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_min": [25, 10, 5],
    "ema_length": [200, 100],
}
DEFAULT_PARAMS = {"rsi_min": 25, "ema_length": 200, "rsi_length": 2, "high_back": 2, "days": 2}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    above = (c >= c.ewm(span=int(p["ema_length"]), adjust=False).mean()).to_numpy()
    buyv = (_rsi(c, int(p["rsi_length"])) <= p["rsi_min"]).to_numpy()
    sellv = (c >= bars_df["high"].shift(int(p["high_back"]))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if not above[i]:
            continue
        b = (not held) and buyv[i]
        if b:
            held = True
        s = sellv[i] and held
        if s:
            held = False
        if b and not s:
            le[i] = True
        elif s and not b:
            lx[i] = True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
