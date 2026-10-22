"""MACD (12, 26, 9) signal crossings, daily bars: a cross up goes long with a stop at the previous bar's low and a target 4 times that distance; a cross down goes short, whose target reuses the long's level
above the price, so each short closes at the next open after its fill; reversing.
Port of FMZ strategy #451030 "MACD双均线交叉策略-MACD-Dual-Moving-Average-Crossover-Strategy" (MACD Strategy (prior-bar stop, 4R target)).

FMZ source id: 451030

Source
    https://www.fmz.com/strategy/451030 (PineScript v4, FMZ last modified 2024-05-11 12:00:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-116), MACD 12 / 26 / 9; stop low[1] / high[1]; target close + 4 (close - low[1]) for both sides
    crossover -> entry Buy, exit(stop = low[1], limit = close + 4 (close - low[1]));  crossunder -> entry Sell, exit(stop = high[1], limit = close + 4 (close - low[1]))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long bracket is set on the signal bar: sl_stop = (close - low[1]) / close and tp_stop = 4 x
      that, shifted one bar inside stops() and re-based on the fill; a signal whose stop is at or above
      the close places no trade. The short's limit is the long formula, a buy limit above the price on
      the wrong side of the market, so the short closes at the first open after its fill bar (the port
      closes it on that bar's signal, as #439872). Daily stop module: mark coarse_bar_stop.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1D" from
      the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long bracket fixed on the signal bar; the short's wrong-side target read as a close.
    2 generic: PASS, MACD signal crossings with a prior-bar stop and a 4R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_451030_macd_cross_prior_bar_stop_4r_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [4.0, 2.0],
    "fast": [12, 8],
}
DEFAULT_PARAMS = {"rr": 4.0, "fast": 12, "slow": 26, "signal": 9}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    sl = (c - bars_df["low"].shift(1)) / c
    xo = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (sl > 0)).to_numpy()   # a stop at or above the close places no trade
    xu = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    m = len(xo)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sfill = 0, -1
    for i in range(m):
        new = pos
        if xo[i] and pos != 1:
            le[i], new = True, 1
        if xu[i] and pos != -1:
            se[i], new = True, -1
            sfill = i + 1
        if pos == -1 and new == -1 and i >= sfill:
            sx[i], new = True, 0                     # wrong-side buy limit: out at the next open
        pos = new
    return le, se, sx, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx, _ = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _, sl = _run(bars_df, p)
    on = pd.Series(le, index=bars_df.index)
    sl_l = sl.where(on)
    return {"sl_stop": sl_l.shift(1), "tp_stop": (sl_l * float(p["rr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
