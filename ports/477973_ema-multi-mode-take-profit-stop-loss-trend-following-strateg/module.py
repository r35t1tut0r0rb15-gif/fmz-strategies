"""The second consecutive bar of a Madrid-ribbon (EMA 5 / 100) and Donchian 20 breakout signal on the EMA 200 side, broker days: long on the second up bar with a stop at its low and a 2 R target, short on the second down bar with a stop at its high and a 2 R target; reversing.
Port of FMZ strategy #477973 "基于EMA马德里带和唐奇安通道的多模式止盈止损趋势跟踪策略-Multi-Mode-Take-Profit-Stop-Loss-Trend-Following-Strategy-Based-on-EMA-Madrid-Ribbon-and-Donchian-Channel" (Pamplona Enhanced TP/SL Toggleable).

FMZ source id: 477973

Source
    https://www.fmz.com/strategy/477973 (PineScript v6, FMZ last modified 2025-01-10 16:24:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-190), EMA 5 / 100 / 200; Donchian 20 (previous bar); risk-reward mode, R:R 2; qty 1
    long_raw = ema5 > ema100 and close > highest(high, 20)[1] and close > ema200;  short_raw = not (ema5 > ema100) and close < lowest(low, 20)[1] and close < ema200;  run counters; count == 2 -> entry
    long: tp = close + 2 (close - low), sl = close - (close - low);  short: tp = close - 2 (high - close), sl = close + (high - close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default risk-reward mode is ported: the stop is the signal bar's low (high) and the target 2
      R from its close, sent as fractions of the fill open (a level at or through it is marketable and
      closed one bar late, as #458256). A new run of signals inside a trade re-sends the bracket on its
      second bar, which is not followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. The fixed qty
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, second-bar trend breakouts with a candle-range bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477973_madrid_donchian20_second_bar_range_bracket_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "dlen": [20, 55],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"dlen": 20, "rr": 2.0}


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


def _second_of_run(flag):
    """True on the second bar of each run of consecutive True values (the script's counter == 2)."""
    f = flag.astype(bool)
    return f & f.shift(1, fill_value=False) & ~f.shift(2, fill_value=False)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e5, e100, e200 = (c.ewm(span=n, adjust=False).mean() for n in (5, 100, 200))
    n = int(p["dlen"])
    green = e5 > e100
    long_raw = green & (c > h.rolling(n).max().shift(1)) & (c > e200)
    short_raw = ~green & (c < lo.rolling(n).min().shift(1)) & (c < e200)
    le, se = _second_of_run(long_raw), _second_of_run(short_raw)
    rr = float(p["rr"])
    rl, rs = c - lo, h - c
    lvl = {"l_sl": c - rl, "l_tp": c + rr * rl, "s_sl": c + rs, "s_tp": c - rr * rs}
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
