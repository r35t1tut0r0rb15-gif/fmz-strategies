"""TEMA 5 / SMA 3 crossings under the SMMA 30, long only, broker days: the TEMA 5 crossing over its SMA 3 while under the SMMA 30 goes long; the cross back under closes only once the close is at least 2 % above
the entry price.
Port of FMZ strategy #439823 "久期均线交叉Renko策略Long-term-Moving-Average-Crossover-Renko-Strategy" (TEMA Cross).

FMZ source id: 439823

Source
    https://www.fmz.com/strategy/439823 (PineScript v2, FMZ last modified 2024-01-24 10:55:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-175), TEMA 5, SMA 3 of TEMA, SMMA 30; min gain 2 %; average and gain protection on
    long = crossover(tema, sma(tema, 3)) and tema < smma 30 and (flat or close <= avg price) -> entry Buy;  close_all when crossunder(tema, sma) and close >= 1.02 x avg price

Interpretation choices (Pine rules in SURVEY_README.md)
    * One position is held (pyramiding 1), so the average-price test matters only from flat (true). The
      average price is the fill open; the close_all needs the 2 % gain on its bar, otherwise the long is
      held. The SMMA uses an SMA seed. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TEMA / SMA crossings and a gain test.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427372 (2 members, best partner #427372, Jaccard 0.740); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439823_tema5_sma3_cross_min_gain_exit_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_gain": [2.0, 0.0],
    "smma_length": [30, 60],
}
DEFAULT_PARAMS = {"min_gain": 2.0, "smma_length": 30, "tema_length": 5, "sma_length": 3}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["tema_length"])
    e1 = c.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    tema = 3 * e1 - 3 * e2 + e3
    s = tema.rolling(int(p["sma_length"])).mean()
    sm = _rma(c, int(p["smma_length"]))
    lc = ((tema > s) & (tema.shift(1) <= s.shift(1)) & (tema < sm)).to_numpy()
    xu = ((tema < s) & (tema.shift(1) >= s.shift(1))).to_numpy()
    gm = float(p["min_gain"]) * 0.01 + 1
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ep = 0, np.nan
    for i in range(m):
        if pos == 1:
            if xu[i] and cv[i] >= gm * ep:
                lx[i], pos = True, 0
        elif lc[i] and i + 1 < m:
            le[i], pos, ep = True, 1, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
