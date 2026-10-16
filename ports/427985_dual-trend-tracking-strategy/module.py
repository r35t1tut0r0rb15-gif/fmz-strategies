"""HPotter combo, broker days: the 123 reversal and an overbought / oversold reading (the 10-bar
stochastic, inverted when the close is below its value 10 bars ago; above 0.92 says long, below 0.5
says short) must agree; long when both say long, short when both say short, flat otherwise.
Port of FMZ strategy #427985 "Dual Trend Tracking Strategy" (Combo 123 Reversal & Overbought/Oversold).

FMZ source id: 427985

Source
    https://www.fmz.com/strategy/427985 (PineScript v4, FMZ last modified 2023-09-27 16:14:25).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 212-252), stoch 14 / K 1 / D 3 / level 50, OO 10, bands 0.92 / 0.5
    123: close[2] < close[1] and close > close[1] and K < D and K > 50 -> 1; mirror -> -1; else hold
    OO: x = stoch(close, high, low, 10); nRes = close > close[10] ? x / 100 : (100 - x) / 100
        nRes < 0.5 -> -1; nRes > 0.92 -> 1; else hold
    both 1 -> entry long; both -1 -> entry short; otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Trade reverse" (default false) is fixed off. strategy.entry reverses: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels only.
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

NAME = "fmz_427985_combo_123_reversal_obos"
FAMILY = "combo_123_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "length_oo": [10, 20],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50,
                  "length_oo": 10, "buy_band": 0.92, "sell_band": 0.5}


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


def _hold(up, dn):
    out = np.zeros(len(up), dtype=np.int8)
    pos = 0
    for i in range(len(up)):
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        out[i] = pos
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def _stoch(h, lo, c, n):
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    return 100 * (c - ll) / (hh - ll)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k = _stoch(h, lo, c, int(p["length"])).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    lv = p["level"]
    r_up = ((c2 < c1) & (c > c1) & (k < d) & (k > lv)).to_numpy()
    r_dn = ((c2 > c1) & (c < c1) & (k > d) & (k < lv)).to_numpy()
    n2 = int(p["length_oo"])
    x = _stoch(h, lo, c, n2)
    res = (x / 100).where(c > c.shift(n2), (100 - x) / 100)
    a, b = _hold(r_up, r_dn), _hold((res > p["buy_band"]).to_numpy(), (res < p["sell_band"]).to_numpy())
    tgt = np.where((a == 1) & (b == 1), 1, np.where((a == -1) & (b == -1), -1, 0)).astype(np.int8)
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
