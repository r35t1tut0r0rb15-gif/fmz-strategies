"""SuperTrend 3 / 10 direction with Stochastic 14 / 3 crossings of 20 / 80, 2-day bars: Pine direction 1 with %K up through 20 goes long, direction -1 with %K down through 80 goes short; the other direction or the other crossing closes; reversing.
Port of FMZ strategy #482805 "动量趋势型SuperTrend与随机指标交叉策略-Momentum-Trend-Following-SuperTrend-and-Stochastic-Crossover-Strategy" (SuperTrend + Stochastic Strategy).

FMZ source id: 482805

Source
    https://www.fmz.com/strategy/482805 (PineScript v5, FMZ last modified 2025-02-20 14:55:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-155), SuperTrend factor 3, ATR 10; Stochastic %K 14 smoothed 3 (%D 3 plot only); levels 80 / 20; 10 % of equity
    direction == 1 and crossover(k, 20) -> entry Long;  direction == -1 and crossunder(k, 80) -> entry Short
    direction == -1 or crossunder(k, 80) -> close Long;  direction == 1 or crossover(k, 20) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's ta.supertrend returns direction 1 in a DOWN-trend and -1 in an up-trend (the source's
      comments say the opposite); ported as written, so the long buys %K's oversold turn while the line
      is above the price. An entry on the other side reverses (REVERSAL INTENDED); a close of the other
      side on that bar is masked by the entry. %D is a plot only. The 10 % of equity size is sizing. Bars
      are blocks of two broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their
      first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend direction with Stochastic level crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482805_supertrend3_10_dir_stoch14_20_80_cross_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "atr_length": [10, 20],
}
DEFAULT_PARAMS = {"factor": 3.0, "atr_length": 10, "k_length": 14, "k_smooth": 3, "ob": 80, "os": 20, "days": 2}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d = _supertrend(bars_df, float(p["factor"]), int(p["atr_length"]))[1]
    n = int(p["k_length"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rng = hh - ll
    k = (100 * (c - ll) / rng.where(rng > 0)).rolling(int(p["k_smooth"])).mean()
    ob, os_ = float(p["ob"]), float(p["os"])
    k_up = (k > os_) & (k.shift(1) <= os_)
    k_dn = (k < ob) & (k.shift(1) >= ob)
    le = (d == 1) & k_up
    se = (d == -1) & k_dn
    lx = (d == -1) | k_dn
    sx = (d == 1) | k_up
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
