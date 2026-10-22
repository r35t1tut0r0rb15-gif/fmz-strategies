"""Separate long and short MACD zero crossings, broker days: the MACD (13, 19) crossing over zero goes long; the MACD (11, 20) having crossed under zero on the previous bar goes short; shorts carry a 21 % stop
and a 20 % target; reversing.
Port of FMZ strategy #439613 "MACD双向优化交易策略MACD-Double-Optimization-Trading-Strategy" (MACD Short/Long Strategy for TradingView Input Optimizer).

FMZ source id: 439613

Source
    https://www.fmz.com/strategy/439613 (PineScript v5, FMZ last modified 2024-01-22 11:10:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 180-331), long: EMA 13 / 19, signal 9, cross point 0, delay 0, signal cross off; short: EMA 11 / 20, signal 9, cross point 0, macd delay 1, signal cross off; long stop / target off; short stop 21 %, target 20 %
    if position <= 0 and long allowed: entry long when crossover(macd_long, 0) (inEntry := true);  if position >= 0 and short allowed and not inEntry: entry short when crossunder(macd_short, 0)[1]
    closes only when one side is disabled (both on: none);  exit(TP/SL Short, limit = avg x 0.80, stop = avg x 1.21);  the long exit has no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * A long signal blocks the short entry on the same bar (inEntry). The short bracket is a fixed 21 % /
      20 % of the average (fill) price, sent once the position exists: the port starts it at the fill
      and reads the stops for short entries only; the state loop follows the same bracket so that the
      next signals see the position the bracket leaves. strategy.equity > 0 is taken as true.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. The 100 % of equity size is sizing. Daily bars are broker days,
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; short bracket fixed from the fill.
    2 generic: PASS, MACD zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_439613_macd_long_short_zero_cross_short_bracket"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_long": [13, 12],
    "slow_long": [19, 26],
}
DEFAULT_PARAMS = {"fast_long": 13, "slow_long": 19, "fast_short": 11, "slow_short": 20, "delay_short": 1,
                  "sl_short": 0.21, "tp_short": 0.20}


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


def _entries(bars_df, p):
    c = bars_df["close"]
    ml = c.ewm(span=int(p["fast_long"]), adjust=False).mean() - c.ewm(span=int(p["slow_long"]), adjust=False).mean()
    ms = c.ewm(span=int(p["fast_short"]), adjust=False).mean() - c.ewm(span=int(p["slow_short"]), adjust=False).mean()
    lc = ((ml > 0) & (ml.shift(1) <= 0)).to_numpy()
    xs = (ms < 0) & (ms.shift(1) >= 0)
    sc = xs.shift(int(p["delay_short"]), fill_value=False).to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    sl, tp = float(p["sl_short"]), float(p["tp_short"])
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == -1 and i >= entry_i:
            x = ov[entry_i]
            if hv[i] >= x * (1 + sl) or lv[i] <= x * (1 - tp):
                pos = 0
        if i + 1 >= m:
            continue
        if pos <= 0 and lc[i]:
            le[i], pos = True, 1
        elif pos >= 0 and sc[i]:
            se[i], pos, entry_i = True, -1, i + 1
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _entries(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, se = _entries(bars_df, p)
    ix = bars_df.index
    on = pd.Series(se, index=ix)
    sl = pd.Series(float(p["sl_short"]), index=ix).where(on)
    tp = pd.Series(float(p["tp_short"]), index=ix).where(on)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
