"""Engulfing-style candles after RSI extremes with a tick bracket, broker days: a bullish candle (close at or over the previous open after a red bar) with the RSI 14 at or under 30 in the last three bars
goes long, the bearish mirror (RSI at or over 70) short; a 20-tick stop and 40-tick target from the signal close; reversing.
Port of FMZ strategy #441057 "蜡烛包裹RSI交易策略Engulfing-Candle-RSI-Trading-Strategy" (EngulfingCandle Strategy).

FMZ source id: 441057

Source
    https://www.fmz.com/strategy/441057 (PineScript v4, FMZ last modified 2024-02-05 11:06:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 187-229), RSI 14 on close (70 / 30); stop 20 ticks, target 40 ticks (x mintick)
    bullish = close >= open[1] and close[1] < open[1];  bearish = close <= open[1] and close[1] > open[1];  signal = (RSI <= 30 now or 1 or 2 bars back and bullish) or (RSI >= 70 ... and bearish)
    signal and bullish -> entry Long, exit(stop = close - 20 mintick, limit = close + 40 mintick);  signal and bearish -> entry Short, exit(stop = close + 20 mintick, limit = close - 40 mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is 20 and 40 ticks from the signal close: 2 and 4 price units at mintick 0.1 on the BTC
      reading; as ATR multiples at the daily ATR(14) reading of about 1000, a stop of 0.002 ATR and a
      target of 0.004 ATR (sl / tp = k ATR / close of the signal bar, shifted one bar inside stops() and
      re-based on the fill). A later signal while held moves the script's levels, which the port does not
      follow. strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on daily bars: mark coarse_bar_stop. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_441057_engulfing_after_rsi_extreme_tick_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_length": [14, 9],
    "oversold": [30, 40],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oversold": 30, "atr_len": 14, "sl_atr": 0.002, "tp_atr": 0.004}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    os_ = float(p["oversold"])
    bull = (c >= o.shift(1)) & (c.shift(1) < o.shift(1))
    bear = (c <= o.shift(1)) & (c.shift(1) > o.shift(1))
    ros, rob = r <= os_, r >= 100 - os_
    nos = ros | ros.shift(1, fill_value=False) | ros.shift(2, fill_value=False)
    nob = rob | rob.shift(1, fill_value=False) | rob.shift(2, fill_value=False)
    sig = (nos & bull) | (nob & bear)
    lsig, ssig = (sig & bull).to_numpy(), (sig & bear).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = o.to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
