"""Donchian (20) breakouts when the channel edge has not been rising, daily bars, with a stop at the signal bar's channel middle and a 5 : 1 target: a close crossing over the previous upper band goes
long, under the previous lower band goes short (each unless already on that side); reversing.
Port of FMZ strategy #449818 "Donchian突破交易策略-Donchian-Breakout-Trading-Strategy" (Donchian New High/Low Strategy [Dillon Grech]).

FMZ source id: 449818

Source
    https://www.fmz.com/strategy/449818 (PineScript v5, FMZ last modified 2024-04-29 14:56:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 121-224), Donchian 20; stop at the basis; target 5 x the stop distance
    flatUpper = upper <= upper[0..19];  long = crossover(close, upper[1]) and flatUpper[1] and position <= 0 -> entry Long;  short mirrored -> entry Short
    basis saved on the signal bar;  dist = |entry price - basis|;  exit(stop = entry -+ dist, limit = entry +- 5 dist)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The loop marks the channel edge "new" only when it is not above any of its last 20 values, as
      written (the comment says the opposite). The stop distance is |fill - basis| with the basis
      saved on the signal bar; the fill is the open of the bar the stop is first read on, so sl_stop =
      |open - basis[signal]| / open on the fill bar and tp_stop = 5 x that: exact, known at the fill's
      open (the exit is sent from the fill bar on, as #440797). Entries only when not already on that
      side, so the levels are fixed per trade. Daily stop module: mark coarse_bar_stop. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; levels from the signal bar's basis and the fill.
    2 generic: PASS, Donchian breakouts with a basis stop and RR target.
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

NAME = "fmz_449818_donchian20_flat_edge_break_basis_stop_rr5_reversal"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "don_length": [20, 55],
    "rr": [5.0, 2.0],
}
DEFAULT_PARAMS = {"don_length": 20, "rr": 5.0}


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


def _channel(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["don_length"])
    up, dn = h.rolling(n).max(), lo.rolling(n).min()
    basis = (up + dn) / 2
    flat_up = pd.Series(True, index=c.index)
    flat_dn = pd.Series(True, index=c.index)
    for i in range(n):
        flat_up &= ~(up > up.shift(i))               # true unless the edge is above one of its last n values
        flat_dn &= ~(dn < dn.shift(i))
    le = (c > up.shift(1)) & (c.shift(1) <= up.shift(2)) & flat_up.shift(1, fill_value=False)
    se = (c < dn.shift(1)) & (c.shift(1) >= dn.shift(2)) & flat_dn.shift(1, fill_value=False)
    return le, se, basis


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _channel(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, basis = _channel(bars_df, p)
    o = bars_df["open"]
    sig_basis = basis.where(le | se).shift(1)         # the basis saved on the signal bar, read on the fill bar
    sl = (o - sig_basis).abs() / o                   # |fill - basis| / fill, known at the fill's open
    return {"sl_stop": sl, "tp_stop": sl * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
