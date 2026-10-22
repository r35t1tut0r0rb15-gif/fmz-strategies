"""SMA 10 / 30 crossings with an RSI 14 filter, daily bars: the cross up with the RSI under 70 goes long, the cross down with the RSI over 30 goes short; reversing (the 50-bar breakout alternatives can never fire).
Port of FMZ strategy #452699 "基于EMA与趋势线突破的双均线-RSI-动量策略-Dual-Moving-Average-RSI-Momentum-Strategy-Based-on-EMA-and-Trendline-Breakouts" (Gold Trading Strategy 15 min).

FMZ source id: 452699

Source
    https://www.fmz.com/strategy/452699 (PineScript v5, FMZ last modified 2024-05-28 11:28:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-155), SMA 10 / 30; RSI 14, levels 70 / 30; breakout lookback 50 (current bar included)
    (crossover(sma10, sma30) or crossover(close, highest(high, 50))) and rsi < 70 -> entry long;  (crossunder(sma10, sma30) or crossunder(close, lowest(low, 50))) and rsi > 30 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * highest(high, 50) includes the current bar, so the close can never cross over it (nor under the
      lowest low): the 'trendline breakout' alternatives never fire, and the port keeps them as written.
      The two entries cannot meet on one bar. There is no exit: positions end at the opposite entry.
      REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SMA crossings with an RSI filter.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452699_sma10_30_cross_rsi_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [10, 20],
    "slow": [30, 50],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "rsi_len": 14, "ob": 70.0, "os": 30.0, "lookback": 50}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["lookback"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    c1 = c.shift(1)
    up = ((f > s) & (f.shift(1) <= s.shift(1))) | ((c > hh) & (c1 <= hh.shift(1)))
    dn = ((f < s) & (f.shift(1) >= s.shift(1))) | ((c < ll) & (c1 >= ll.shift(1)))
    le = up & (r < float(p["ob"]))
    se = dn & (r > float(p["os"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
