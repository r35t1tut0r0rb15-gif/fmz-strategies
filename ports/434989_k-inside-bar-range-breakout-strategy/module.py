"""Previous-bar breakouts with an ATR bracket, broker days: a close above the previous high (with the low above the 20-bar low)
goes long with the stop 2 ATR 14 under the bar's low and the target 3 ATR above its high; a close below the previous low
(with the high under the 20-bar high) goes short with the mirror bracket (reversing).
Port of FMZ strategy #434989 "突破重叠K线高低位策略Inside-Bar-Range-Breakout-Strategy" (Inside Bar Range Breakout Strategy).

FMZ source id: 434989

Source
    https://www.fmz.com/strategy/434989 (PineScript v5, FMZ last modified 2023-12-11 15:16:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-189), look back 20; ATR 14; SL 2 ATR from the low / high, TP 3 ATR from the high / low
    longEntry = close > high[1] and low > lowest(low, 20) -> entry long, exit(stop = low - 2 atr, limit = high + 3 atr)
    shortEntry = close < low[1] and high < highest(high, 20) -> entry short, exit(stop = high + 2 atr, limit = low - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The inside-bar test and the exit conditions are computed but never used. The levels come
      from the signal bar and are ported as fractions of the signal close, shifted one bar inside
      stops() (re-based on the fill). A repeated signal inside the trade re-issues the levels: not
      expressible (mark trailing_stop_pending); the opening levels are kept.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on daily bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-issued levels approximated).
    2 generic: PASS, bar breakouts and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434989_bar_breakout_atr_bracket"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 1.0],
    "tp_mult": [3.0, 1.5],
}
DEFAULT_PARAMS = {"lookback": 20, "atr_len": 14, "sl_mult": 2.0, "tp_mult": 3.0}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    k = int(p["lookback"])
    le = ((c > h.shift(1)) & (lo > lo.rolling(k).min())).to_numpy()
    se = ((c < lo.shift(1)) & (h < h.rolling(k).max())).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    a, b = float(p["sl_mult"]), float(p["tp_mult"])
    with np.errstate(invalid="ignore"):
        sl = np.where(le, (cv - lv + a * atr) / cv, np.where(se, (hv - cv + a * atr) / cv, np.nan))
        tp = np.where(le, (hv + b * atr - cv) / cv, np.where(se, (cv - lv + b * atr) / cv, np.nan))
    return le, se, sl, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
