"""Alligator lips / teeth crossings with the Awesome and Accelerator oscillators, daily bars: the lips (SMA 5, 3 bars back) crossing over the teeth (SMA 8, 5 bars back) with AO and AC over 0 goes long, stopped at the 5-bar low with a 2 R target; the mirror goes short; reversing.
Port of FMZ strategy #474050 "Multi Indicator Crossover Momentum Trend Following Strategy with Optimized Take Profit and Stop Loss System" (Alligator with AO and AC Strategy).

FMZ source id: 474050

Source
    https://www.fmz.com/strategy/474050 (PineScript v5, FMZ last modified 2024-12-05 16:21:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 100-175), jaw 13/8, teeth 8/5, lips 5/3 (SMA, shifted back); AO 5 / 34 of hl2; AC = AO - SMA 5; stop at the 5-bar low / high, target 2 R; 10 % of equity
    crossover(lips, teeth) and ao > 0 and ac > 0 -> stop = lowest(low, 5), tp = close + 2 (close - stop), entry Long + exit;  crossunder and ao < 0 and ac < 0 -> stop = highest(high, 5), tp = close - 2 (stop - close), entry Short + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The offsets read past values (sma[offset]), not forward plots. The 5-bar extremes include the
      signal bar. The bracket is sent once, on the signal bar: sent as fractions of the fill open; a
      level at or through it is marketable and closed one bar late (as #458256). Crossings alternate,
      so no repeat signal re-sends it. The jaw feeds no order. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The equity share is
      not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, Alligator crossings with AO / AC filters and a swing bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_474050_alligator_lips_teeth_cross_ao_ac_swing_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lips_len": [5, 3],
    "teeth_len": [8, 13],
}
DEFAULT_PARAMS = {"lips_len": 5, "teeth_len": 8, "lips_off": 3, "teeth_off": 5}


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
    lips = c.rolling(int(p["lips_len"])).mean().shift(int(p["lips_off"]))
    teeth = c.rolling(int(p["teeth_len"])).mean().shift(int(p["teeth_off"]))
    mp = (h + lo) / 2
    ao = mp.rolling(5).mean() - mp.rolling(34).mean()
    ac = ao - ao.rolling(5).mean()
    le = (lips > teeth) & (lips.shift(1) <= teeth.shift(1)) & (ao > 0) & (ac > 0)
    se = (lips < teeth) & (lips.shift(1) >= teeth.shift(1)) & (ao < 0) & (ac < 0)
    ll, hh = lo.rolling(5).min(), h.rolling(5).max()
    lvl = {"l_sl": ll, "l_tp": c + (c - ll) * 2, "s_sl": hh, "s_tp": c - (hh - c) * 2}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se, se, sf & s_thr & ~le


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
