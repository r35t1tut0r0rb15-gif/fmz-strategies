"""Stochastic (14, 3, 3) crossings in an EMA 50 / 150 trend, daily bars: in an up-trend a %K cross over %D under 30 goes long with the 5-bar low as stop and a 2 R target; the down-trend mirror over 70 goes short; reversing.
Port of FMZ strategy #474964 "Dual EMA Stochastic Trend Following Trading Strategy" (EMA-Stochastic Strategy).

FMZ source id: 474964

Source
    https://www.fmz.com/strategy/474964 (PineScript v5, FMZ last modified 2024-12-13 10:48:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 177-239), EMA 50 / 150; stochastic 14, K 3, D 3; stop at the 5-bar low / high; target 2 R from the signal close
    close > ema50 > ema150 and k < 30 and crossover(k, d) -> sl := lowest(low, 5), tp := close + 2 (close - sl), entry Buy + exit;  mirror -> entry Sell + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 5-bar extremes include the signal bar. The bracket is sent on each signal bar: the opening
      signal's levels are ported, sent as fractions of the fill open (a level at or through it is
      marketable and closed one bar late, as #458256); a repeat signal inside a trade re-sends it and is
      not followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, trend stochastic crossings with a swing bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474964_ema50_150_trend_stoch_cross_swing_bracket_reversal"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [50, 20],
    "slow": [150, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 150}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    a = c.ewm(span=int(p["fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["slow"]), adjust=False).mean()
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    k = (100 * (c - ll) / (hh - ll)).rolling(3).mean()
    d = k.rolling(3).mean()
    le = (c > a) & (c > b) & (a > b) & (k < 30) & (k > d) & (k.shift(1) <= d.shift(1))
    se = (c < a) & (c < b) & (a < b) & (k > 70) & (k < d) & (k.shift(1) >= d.shift(1))
    l_sl, s_sl = lo.rolling(5).min(), h.rolling(5).max()
    lvl = {"l_sl": l_sl, "l_tp": c + 2 * (c - l_sl), "s_sl": s_sl, "s_tp": c - 2 * (s_sl - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
