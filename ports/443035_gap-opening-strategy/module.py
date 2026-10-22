"""Range expansion above a rising SMA 20, daily bars, long only: the close above the SMA and its previous value with the 3-bar range above its 20-bar average goes long; a low more than 2 % under the close
closes.
Port of FMZ strategy #443035 "Gap Opening Strategy" (HL MA Crypto Strategy-Ortiz).

FMZ source id: 443035

Source
    https://www.fmz.com/strategy/443035 (PineScript v5, FMZ last modified 2024-02-28 17:12:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-168), SMA 20; HL length 3; exit below 0.98 x close; short side off (false)
    long = close > ma and close > ma[1] and (highest(high, 3) - lowest(low, 3)) > sma(that, 20) -> entry Buy;  low < close x 0.98 -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit compares the bar's own low with its own close (a lower wick over 2 %), read at the close
      and filled at the next open; it acts only on a held long, so a same-bar entry stands. The short
      condition is the constant false. Long only. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range expansion with an SMA filter; lower-wick exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_443035_range_expansion_sma20_wick_exit_long"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [20, 50],
    "exit_below": [0.98, 0.95],
}
DEFAULT_PARAMS = {"ma_length": 20, "exit_below": 0.98, "hl_length": 3}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ma_length"])
    ma = c.rolling(n).mean()
    k = int(p["hl_length"])
    hl = h.rolling(k).max() - lo.rolling(k).min()
    go = ((c > ma) & (c > ma.shift(1)) & (hl > hl.rolling(n).mean())).to_numpy()
    out = (lo < c * float(p["exit_below"])).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
