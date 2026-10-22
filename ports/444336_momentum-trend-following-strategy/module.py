"""Aroon crossings with unequal lengths, daily bars, long only: the Aroon up (56) crossing over the Aroon down (20) with the down line at 5 or more goes long; the up line crossing back under closes (the short
side is switched off by the trade-direction input).
Port of FMZ strategy #444336 "Momentum Trend Following Strategy" (Aroon and ASH strategy - ETHERIUM [IkkeOmar]).

FMZ source id: 444336

Source
    https://www.fmz.com/strategy/444336 (PineScript v5, FMZ last modified 2024-03-11 10:54:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 129-265), Aroon long side: up 56, down 20; short side 17 / 55 (off); ASH length 9 (unused); trade direction Long; start 2018 (always true); 100 % of equity
    upper = 100 (highestbars(high, 57) + 56) / 56;  lower = 100 (lowestbars(low, 21) + 20) / 20
    crossover(upper, lower) and lower >= 5 -> entry long (from flat);  long and crossunder(upper, lower) -> close long (short_signal never set: shorts off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * highestbars / lowestbars give the offset of the newest extreme in the window (as #439696). The
      trade direction is Long, so shortCondition is never true, short_signal stays false and the
      close-and-reverse branches only close the long. The script's state flags follow the orders
      exactly. The Ahrens average is computed but never used. Long only. The 100 % of equity size is
      sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Aroon line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only; ETHERIUM in the title only).
    4 signals only: the 100 % of equity size stored.
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

NAME = "fmz_444336_aroon_56_20_cross_long"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_upper": [56, 25],
    "len_lower": [20, 25],
}
DEFAULT_PARAMS = {"len_upper": 56, "len_lower": 20, "floor": 5.0}


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
    h, lo = bars_df["high"], bars_df["low"]
    nu, nl = int(p["len_upper"]), int(p["len_lower"])
    hb = -h.rolling(nu + 1).apply(lambda a: np.argmax(a[::-1]), raw=True)     # highestbars: offset of the newest high
    lb = -lo.rolling(nl + 1).apply(lambda a: np.argmin(a[::-1]), raw=True)
    up = 100 * (hb + nu) / nu
    dn = 100 * (lb + nl) / nl
    go = ((up > dn) & (up.shift(1) <= dn.shift(1)) & (dn >= float(p["floor"]))).to_numpy()
    out = ((up < dn) & (up.shift(1) >= dn.shift(1))).to_numpy()
    m = len(go)
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
