"""QuantCat momentum finder: the close crossing above the EMA (20, 40 or 60) that it has crossed
least often in 60 bars (fewer than 2 times), with RSI(14) between 50 and 60 and a bullish MACD,
goes long; the mirror goes short. Each entry carries a stop 0.6 and a target 2.2 daily ATR(14)
from the signal close.
Port of FMZ strategy #426854 "Quantitative Momentum Trend Trading Strategy".

Source
    https://www.fmz.com/strategy/426854 (PineScript v2/v3 syntax, FMZ last modified 2023-09-14 20:38:49).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 130-254), lookback 60, EMA 20 / 40 / 60, max 2 crosses
    sums of close crossing over / under each EMA in the last 60 bars
    bull cross on EMA k: its sum is the smallest of the three and < 2, crossover(close, ema k),
        50 < rsi(14) < 60, macd > signal and macd > -0.5 (the first matching EMA wins)
    bear mirrors (rsi 40-50, macd < signal and < 0.5); as written the 40-EMA bear test compares
        its crossunder sum with the 60-EMA crossOVER sum
    long -> entry long, stop = close - 0.6 atrD, target = close + 2.2 atrD (fixed while held)
    atrD = security('D', atr(14))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The daily ATR runs on broker days built from the hourly bars. Historical lookahead_off
      values are the last completed day's (the new day's value from the bar whose end reaches
      the day's 17:00 New York close).
    * Criterion 2: the levels are ATR multiples already; as fractions of the signal close they
      are applied to the fill (sl_stop / tp_stop shifted one bar). They are set only when not
      already in the same direction, as the engine does at the fill.
    * The macd thresholds (+-0.5) are price units (0 ATR on BTC); kept as written.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "1h" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426854_quantcat_momentum"
FAMILY = "momentum_breakout"  # proposed 2026-10-07, user to confirm
FREQ = "1h"  # backtest header period: 1h
BAR_HOURS = 1
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_mult": [0.6, 1.0],
    "target_mult": [1.5, 2.2],
    "lookback": [40, 60],
}
DEFAULT_PARAMS = {"lookback": 60, "max_cross": 2, "stop_mult": 0.6, "target_mult": 2.2, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily_atr(bars_df, n):
    day = broker_day(bars_df.index)
    daily = bars_df.groupby(day).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    datr = _atr_pine(daily, n)
    end_ny = (bars_df.index + pd.Timedelta(hours=BAR_HOURS)).tz_convert("America/New_York")
    day_end_ny = (pd.DatetimeIndex(day) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    at_close = np.asarray(end_ny >= day_end_ny)
    return np.where(at_close, datr.reindex(day).to_numpy(), datr.shift(1).reindex(day).to_numpy())


def _signals(bars_df, p):
    c = bars_df["close"]
    lb = int(p["lookback"])
    xo, xu, s_o, s_u = {}, {}, {}, {}
    for n in (20, 40, 60):
        e = c.ewm(span=n, adjust=False).mean()
        xo[n] = (c > e) & (c.shift(1) <= e.shift(1))
        xu[n] = (c < e) & (c.shift(1) >= e.shift(1))
        s_o[n] = xo[n].astype(float).rolling(lb).sum()
        s_u[n] = xu[n].astype(float).rolling(lb).sum()
    rsi = _rsi_pine(c, 14)
    ema = lambda x, n: x.ewm(span=n, adjust=False).mean()
    macd = ema(c, 12) - ema(c, 26)
    sig = ema(macd, 9)
    bull_m = (macd > sig) & (macd > -0.5)
    bear_m = (macd < sig) & (macd < 0.5)
    rb = (rsi > 50) & (rsi < 60) & bull_m
    rs = (rsi < 50) & (rsi > 40) & bear_m
    k = p["max_cross"]
    b25 = (s_o[20] < s_o[40]) & (s_o[20] < s_o[60]) & (s_o[20] < k) & xo[20] & rb
    b50 = (s_o[40] < s_o[20]) & (s_o[40] < s_o[60]) & (s_o[40] < k) & xo[40] & rb & ~b25
    b75 = (s_o[60] < s_o[20]) & (s_o[60] < s_o[40]) & (s_o[60] < k) & xo[60] & rb & ~b25 & ~b50
    s25 = (s_u[20] < s_u[40]) & (s_u[20] < s_u[60]) & (s_u[20] < k) & xu[20] & rs
    s50 = (s_u[40] < s_u[20]) & (s_u[40] < s_o[60]) & (s_u[40] < k) & xu[40] & rs & ~s25
    s75 = (s_u[60] < s_u[20]) & (s_u[60] < s_u[40]) & (s_u[60] < k) & xu[60] & rs & ~s25 & ~s50
    return (b25 | b50 | b75), (s25 | s50 | s75)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    frac = pd.Series(_daily_atr(bars_df, int(p["atr_len"])), index=bars_df.index) / bars_df["close"]
    f = frac.where(le | se)
    return {"sl_stop": (p["stop_mult"] * f).shift(1), "tp_stop": (p["target_mult"] * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
