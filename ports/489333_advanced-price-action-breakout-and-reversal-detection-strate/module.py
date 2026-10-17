"""Pin bars or five-close breakouts with a pip bracket, broker days: a bullish "pin bar" (a long upper wick, as written)
or a close above the highest of the previous five closes goes long; the bearish mirror goes short; each trade has a
stop and a target three times as far (pips in the source, ATR multiples here).
Port of FMZ strategy #489333 "高级价格行情突破与反转检测策略-Advanced-Price-Action-Breakout-and-Reversal-Detection-Strategy" (Price Action Bot - EUR/USD).

FMZ source id: 489333

Source
    https://www.fmz.com/strategy/489333 (PineScript v6, FMZ last modified 2025-04-03 15:09:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-210), RR 3, SL 10 pips (pip = 10 ticks), trail switch on
    allowTrade = hour != 13 and hour != 14
    bullPin = close > open and (high - close) > 2 x (close - open);  bearPin = open > close and (close - low) > 2 x (open - close)
    long = allowTrade and (bullPin or close > highest(close[1], 5));  short = allowTrade and (bearPin or close < lowest(close[1], 5))
    exit("TP/SL", stop = close -+ 10 pips, limit = close +- 30 pips, trail_points = 5 pips)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 10-pip stop becomes sl_atr x Wilder ATR(14) of the signal bar. The title names EUR/USD, where
      10 pips are about 0.15 of a daily ATR (on the backtest's BTC_USDT 10 pips of 0.1 ticks are 10 USD, a negligible
      0.004 ATR); 0.15 is used (judgement before any backtest). tp_stop = 3 x the stop; shifted one bar inside
      stops(), re-based on the fill.
    * trail_points without trail_offset starts no trailing stop in Pine: inert, not emitted.
    * Session open (check 9 / C6): hours 13-14 are excluded in the chart's time zone; a daily bar (stamped at the
      broker-day start, 21:00 / 22:00 UTC) is never in them, so the filter is always true; not emitted.
    * Every signal bar is an entry; entries reverse (REVERSAL INTENDED). On a bar with both signals the short (written
      last) wins, and the shared exit id binds to it.
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header: coarse_bar_stop.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, pip distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 2 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: hours 13-14 excluded in the chart's time zone, never a daily bar's hour; not emitted.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_489333_pin_bar_or_close_breakout_bracket"
FAMILY = "price_action_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.15, 0.5],
    "rr": [3.0, 1.5],
}
DEFAULT_PARAMS = {"sl_atr": 0.15, "rr": 3.0, "breakout": 5, "atr_len": 14}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["breakout"])
    bull_pin = (c > o) & ((h - c) > 2 * (c - o))
    bear_pin = (o > c) & ((c - lo) > 2 * (o - c))
    long_c = bull_pin | (c > c.shift(1).rolling(n).max())
    short_c = (bear_pin | (c < c.shift(1).rolling(n).min())).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return (long_c & ~short_c).astype(bool), false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": (p["rr"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
