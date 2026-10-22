"""Close crossings of the EMA 21 in the EMA 21 / 200 trend, daily bars: in an up trend a close rising over the previous close that also crosses over the EMA 21 goes long, in a down trend the mirror goes short, each with a 55-tick target and 30-tick stop; a long closes when the trend turns down or the close crosses under the EMA 21, a short on the mirror; reversing.
Port of FMZ strategy #468324 "动态趋势跟踪EMA交叉策略-Dynamic-Trend-Following-EMA-Crossover-Strategy" (gucci 1.0).

FMZ source id: 468324

Source
    https://www.fmz.com/strategy/468324 (PineScript v5, FMZ last modified 2024-09-26 15:41:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-242), 1-minute request.security open / close (the chart bar's last minute); high / low of 2 closes; EMA 21 / 200 of that close; target 55, stop 30 ticks; trail_offset 25 x mintick
    ema21 > ema200 and crossover(close, lowest(close, 2)) and crossover(close, ema21) -> entry Long + exit(limit = close + 55 ticks, stop = close - 30 ticks, trail_offset = 2.5)
    ema21 < ema200 and crossunder(close, highest(close, 2)) and crossunder(close, ema21) -> entry Short + exit (mirrored)
    ema21 < ema200 or crossunder(close, ema21) -> close Long;  ema21 > ema200 or crossover(close, ema21) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "1" request on a daily chart reads the chart bar's last 1-minute bar (#436765): its close is
      the daily close (its open only plotted). crossover(close, lowest(close, 2)) is a close over the
      previous close after one at or under the close before it. The 55 / 30 ticks are 5.5 / 3 at the
      0.1 tick, ported as ATR multiples at the daily reading (~1000): 0.0055 / 0.003 ATR 14 from the bar
      before the fill. trail_offset without trail_price / trail_points places no trailing stop
      (#441084). The closes follow the entries and act only on a position held into the bar and not
      being reversed (#437773). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on
      daily bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, EMA crossings in an EMA trend with trend-change exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_468324_close_cross_ema21_in_ema200_trend_tick_bracket_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_fast": [21, 55],
    "tp_atr": [0.0055, 2.0],
    "sl_atr": [0.003, 1.0],
}
DEFAULT_PARAMS = {"ema_fast": 21, "ema_slow": 200, "tp_atr": 0.0055, "sl_atr": 0.003, "atr_len": 14, "hl": 2}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _x(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    k = int(p["hl"])
    hi, lw = c.rolling(k).max(), c.rolling(k).min()
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    bull, bear = ef > es, ef < es
    le = bull & _x(c, lw) & _x(c, ef)
    se = bear & _x(hi, c) & _x(ef, c)
    lx = (bear | _x(ef, c)) & ~se             # a close on a reversal bar gives way to the reversal
    sx = (bull | _x(c, ef)) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
