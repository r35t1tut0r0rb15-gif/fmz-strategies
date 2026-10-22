"""RSI 13 above its SMA 13 and rising two bars, with three higher highs, broker days, long only: such a bar buys; the close crossing under the SMA 55 closes.
Port of FMZ strategy #477550 "RSI趋势突破与动量增强交易策略-RSI-Trend-Breakthrough-and-Momentum-Enhancement-Trading-Strategy" (Improved Strategy with RSI Trending Upwards).

FMZ source id: 477550

Source
    https://www.fmz.com/strategy/477550 (PineScript v5, FMZ last modified 2025-01-06 13:43:48).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-176), RSI 13, SMA 13 of RSI; SMA 21 / 55 / 144 (55 used); qty 10 % of equity / close; date filter from 2007
    rsi > sma(rsi, 13) and rsi > rsi[1] > rsi[2] and high > high[1] > high[2] > high[3] -> entry Long;  crossunder(close, sma55) or (crossunder(rsi, avg) and crossunder(close, sma55)) -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second sell clause needs the close crossing under the SMA 55 too, so the sell condition is that
      crossing alone. The date filter is always true on the data. The other SMA / downtrend tests are not
      used. Long only. The 10 % of equity qty is sizing. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, rising RSI with higher highs; SMA 55 exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity qty stored, not ported.
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

NAME = "fmz_477550_rising_rsi13_higher_highs_sma55_exit_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [13, 21],
    "exit_ma": [55, 21],
}
DEFAULT_PARAMS = {"rsi_length": 13, "rsi_avg_length": 13, "exit_ma": 55}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, c = bars_df["high"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    ra = r.rolling(int(p["rsi_avg_length"])).mean()
    rising = (r > r.shift(1)) & (r.shift(1) > r.shift(2))
    hh = (h.shift(2) > h.shift(3)) & (h.shift(1) > h.shift(2)) & (h > h.shift(1))
    le = (r > ra) & rising & hh
    ma = c.rolling(int(p["exit_ma"])).mean()
    lx = (c < ma) & (c.shift(1) >= ma.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
