"""HPotter combo of the 123 reversal and the previous day's floor pivots, 1-hour bars: long while both say up, short while
both say down, flat otherwise. The pivot side is up after a close above R1 = 2 PP - L and down after a close below
S1 = 2 PP - H of the last completed broker day.
Port of FMZ strategy #434678 "Reversal Dynamic Pivot Points Exponential Moving Average Strategy" (Combo Backtest 123 Reversal & Dynamic Pivot Point).

FMZ source id: 434678

Source
    https://www.fmz.com/strategy/434678 (PineScript v4, FMZ last modified 2023-12-08 11:37:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 209-247), stoch 14 / 1 / 3, level 50; daily high[1] / low[1] / close[1]; reverse false
    p123 as Reversal123(14, 1, 3, 50);  PP = (H + L + C) / 3 (security 'D', x[1]);  dpp = close > 2 PP - L ? 1 : close < 2 PP - H ? -1 : dpp[1]
    both 1 -> entry long;  both -1 -> entry short;  otherwise close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', x[1]) is read as the last completed broker day (17:00 America/New_York), as
      #428790, built from the port's own bars. Each side keeps its last state until it changes.
      strategy.entry reverses: REVERSAL INTENDED. reverse is false. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, oscillator levels and prior-day pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG434678 (2 members, best partner #439113, Jaccard 0.807); ND431662 (2 members, best partner #431662, Jaccard 0.665); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily pivots on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434678_combo_123_daily_pivot"
FAMILY = "combo_123_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 7],
    "level": [50, 30],
}
DEFAULT_PARAMS = {"length": 14, "k_smoothing": 1, "d_length": 3, "level": 50}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _hold(cond_up, cond_dn):
    m = len(cond_up)
    out = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if cond_up[i]:
            q = 1
        elif cond_dn[i]:
            q = -1
        out[i] = q
    return out


def _prev_day(bars_df):
    """High, low and close of the last completed broker day, on every bar of the next one."""
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    return tuple(d[k].reindex(day).to_numpy() for k in ("high", "low", "close"))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smoothing"])).mean()
    d = k.rolling(int(p["d_length"])).mean()
    c1, c2 = c.shift(1), c.shift(2)
    p123 = _hold(((c2 < c1) & (c > c1) & (k < d) & (k > p["level"])).to_numpy(),
                 ((c2 > c1) & (c < c1) & (k > d) & (k < p["level"])).to_numpy())
    dh, dl, dc = _prev_day(bars_df)
    pp = (dh + dl + dc) / 3
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        dpp = _hold(cv > 2 * pp - dl, cv < 2 * pp - dh)
    tgt = np.where((p123 == 1) & (dpp == 1), 1, np.where((p123 == -1) & (dpp == -1), -1, 0)).astype(np.int8)
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
