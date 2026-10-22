"""New 20-bar closing highs with a five-bar decay, daily bars, long only: a new high of the 20-bar highest close goes long; five bars without a new high close the trade (shorting is off by default).
Port of FMZ strategy #442621 "Reversal Momentum Breakout Strategy" (New Highs and Lows Momentum Strategy).

FMZ source id: 442621

Source
    https://www.fmz.com/strategy/442621 (PineScript v5, FMZ last modified 2024-02-23 12:11:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-232), window 20; decay 5; start date (dropped); allow shorting off; 100 % of equity
    highest(close, 20) > highest(close, 20)[1] -> counter = 5, high period on;  else counter > 0 -> counter - 1, else high period off
    high period and counter == 5 -> entry Long;  high period and counter == 0 -> close Long;  (lows mirrored, short side off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A new high while long is refused (default pyramiding) and restarts the count, so the long is held
      until five bars pass with no new 20-bar closing high. The short side needs "Allow shorting", off by
      default. The start date is dropped. Long only. The 100 % of equity size is sizing. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, new-high momentum with a decay count.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
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

NAME = "fmz_442621_new_closing_high_decay_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "window": [20, 50],
    "decay": [5, 10],
}
DEFAULT_PARAMS = {"window": 20, "decay": 5}


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
    c = bars_df["close"]
    wh = c.rolling(int(p["window"])).max()
    nh = (wh > wh.shift(1)).to_numpy()
    dk = int(p["decay"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cnt, is_h, held = 0, False, False
    for i in range(m):
        if nh[i]:
            cnt, is_h = dk, True
        elif cnt > 0:
            cnt -= 1
        else:
            is_h = False
        if is_h and cnt == dk and not held:
            le[i] = True
        elif is_h and cnt == 0 and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
