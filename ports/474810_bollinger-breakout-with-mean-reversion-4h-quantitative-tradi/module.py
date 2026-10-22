"""Bollinger 20 / 2 breakout candles, daily bars, entries only from flat: a green candle whose body midpoint is over the upper band buys with a stop at its low; a red candle with the midpoint under the lower band sells with a stop at its high; a red candle opening and closing back under the upper band closes the long, the mirror closes the short.
Port of FMZ strategy #474810 "Bollinger Breakout with Mean Reversion 4H Quantitative Trading Strategy" (Bollinger 4H Follow).

FMZ source id: 474810

Source
    https://www.fmz.com/strategy/474810 (PineScript v5, FMZ last modified 2024-12-12 11:24:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-150), BB 20, 2 sd; stop at the signal bar's low / high; size equity x 3 / close; commission 0.04 %
    flat and close > open and (close + open) / 2 > upper -> entry Long, exit(stop = low);  flat and close < open and (close + open) / 2 < lower -> entry Short, exit(stop = high);  long and close < upper and open < upper and close < open -> close Long;  short mirror -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the signal bar's own low / high, sent once on the signal bar: sent as a fraction of
      the fill open (a level at or through it is marketable and closed one bar late). Entries only from
      flat: a loop follows the stop on the bar's low / high and the close tests so the flat gate lines up
      (as 449508). Opposite entries cannot occur. The leveraged size and commission are not ported. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. FREQ = "1D"
      from the backtest header (broker days; the title's "4H" is not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the signal bar's extreme as the stop.
    2 generic: PASS, band breakout candles with candle-colour exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leveraged equity size and commission stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_474810_bb20_breakout_candle_bar_extreme_stop_from_flat"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    mid = (c + o) / 2
    lc = ((c > o) & (mid > up)).to_numpy()
    sc = ((c < o) & (mid < dn)).to_numpy()
    xl = ((c < up) & (o < up) & (c < o)).to_numpy()
    xs = ((c > dn) & (o > dn) & (c > o)).to_numpy()
    ov, hv, lv = (z.to_numpy(dtype=float) for z in (o, h, lo))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, side = np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, sl_n = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl = pend, 0, sl_n
            if (pos == 1 and sl >= ov[i]) or (pos == -1 and sl <= ov[i]):
                if pos == 1:
                    lx[i] = True                 # the stop through the fill: closed at the next open
                else:
                    sx[i] = True
                pend, sl = 2, np.nan
        elif pend in (2, 3):
            pos, pend, sl = 0, 0, np.nan
        if pos == 1 and lv[i] <= sl:
            pos, sl = 0, np.nan                  # the stop fills inside this bar
        elif pos == -1 and hv[i] >= sl:
            pos, sl = 0, np.nan
        if pend != 0:
            continue
        if pos == 0 and lc[i]:
            sl_n = lv[i]
            le[i], pend, sl_sent[i], side[i] = True, 1, sl_n, 1
        elif pos == 0 and sc[i]:
            sl_n = hv[i]
            se[i], pend, sl_sent[i], side[i] = True, -1, sl_n, -1
        elif pos == 1 and xl[i]:
            lx[i], pend = True, 3
        elif pos == -1 and xs[i]:
            sx[i], pend = True, 3
    ix = bars_df.index
    return [pd.Series(z, index=ix) for z in (le, lx, se, sx, sl_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, sd = sl_l.shift(1), sd.shift(1)       # the signal bar's stop, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
