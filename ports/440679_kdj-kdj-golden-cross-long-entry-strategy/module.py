"""KDJ crossings, broker days, long only: the J line crossing above the D line (KDJ 9 / 3) goes long; J above 100 closes.
Port of FMZ strategy #440679 "KDJ阳线突破买入策略KDJ-Golden-Cross-Long-Entry-Strategy" (KDJ).

FMZ source id: 440679

Source
    https://www.fmz.com/strategy/440679 (PineScript v5, FMZ last modified 2024-02-01 10:28:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-208), period 9, signal 3; profit / stop margins (in a commented-out exit); dates 2023-01 to 2024-01
    RSV = 100 (close - lowest(low, 9)) / (highest(high, 9) - lowest(low, 9));  K = bcwsma(RSV, 3, 1);  D = bcwsma(K, 3, 1);  J = 3K - 2D;  bcwsma = (s + 2 nz(prev)) / 3
    crossunder(D, J) and in range -> entry S (long);  J > 100 and in range -> close S

Interpretation choices (Pine rules in SURVEY_README.md)
    * The smoothing keeps the script's nz() start (0 before the first value). The exit with the margins
      is commented out. The author's bounded date window is dropped. The close acts only on a held long:
      on a bar with both, an entry from flat still fills. Long only. No sizing code. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, KDJ lines.
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

NAME = "fmz_440679_kdj_j_over_d_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ilong": [9, 14],
    "isig": [3, 5],
}
DEFAULT_PARAMS = {"ilong": 9, "isig": 3}


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


def _bcwsma(x, l, mw):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (mw * v[i] + (l - mw) * (0.0 if np.isnan(prev) else prev)) / l
        prev = out[i]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n, s = int(p["ilong"]), int(p["isig"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rsv = 100 * (c - ll) / (hh - ll).where(hh > ll)
    k = _bcwsma(rsv, s, 1)
    d = _bcwsma(k, s, 1)
    j = 3 * k - 2 * d
    buy = ((d < j) & (d.shift(1) >= j.shift(1))).to_numpy()
    sell = (j > 100).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = 1 if buy[i] else pos
        if sell[i] and pos == 1 and new == 1:
            new = 0
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
