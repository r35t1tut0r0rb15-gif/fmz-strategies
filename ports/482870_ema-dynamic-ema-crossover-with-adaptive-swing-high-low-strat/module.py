"""Close crossing above EMA 22 bought, any close below EMA 22 shorted, with the 14-bar swing extremes as stop and
target, daily (broker-day) bars: a close crossing above EMA 22 goes long (target the 14-bar high, stop the 14-bar low);
a close below EMA 22 goes short (target the 14-bar low, stop the 14-bar high).
Port of FMZ strategy #482870 "动态-EMA-交叉摆动高低点自适应策略-Dynamic-EMA-Crossover-with-Adaptive-Swing-High-Low-Strategy" (22 EMA Crossover Strategy).

FMZ source id: 482870

Source
    https://www.fmz.com/strategy/482870 (PineScript v6, FMZ last modified 2025-02-27 17:32:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 107-146), EMA 22, swing lookbacks 14 / 14
    buy = crossover(close, ema22) and close > ema22 -> entry + exit(limit = highest(high, 14), stop = lowest(low, 14))
    sell = crossunder(close, ema22) or close < ema22 -> entry short + exit(limit = lowest low, stop = highest high)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: long sl = (close - lowest low 14) / close,
      tp = (highest high 14 - close) / close (short mirrored), picked by the signal's side, shifted one bar inside
      stops() and re-based on the fill (house rule). A signal whose stop or target is not beyond the close emits no
      entry (as #490798).
    * Every close below EMA 22 is a sell signal, so a held short has its bracket re-placed each bar: mark
      trailing_stop_pending; the port keeps the entry's bracket.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00
      America/New_York) stamped with their first minute (as #430984); stops on daily bars: coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, an EMA and rolling swing extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND482870 (2 members, best partner #483066, Jaccard 0.746); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482870_ema22_cross_swing_bracket_1d"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [22, 50],
    "swing_len": [14, 20],
}
DEFAULT_PARAMS = {"ema_len": 22, "swing_len": 14}


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
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    n = int(p["swing_len"])
    up, dn = (h.rolling(n).max() - c) / c, (c - lo.rolling(n).min()) / c
    ok = (up > 0) & (dn > 0)
    long_e = ((c > ema) & (c.shift(1) <= ema.shift(1)) & ok).astype(bool)
    short_e = ((c < ema) & ok & ~long_e).astype(bool)
    return long_e, short_e, up, dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e, _, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, _, up, dn = _signals(bars_df, p)
    return {"sl_stop": dn.where(long_e, up).shift(1), "tp_stop": up.where(long_e, dn).shift(1)}


def portfolio_kwargs(**params):
    return {}
