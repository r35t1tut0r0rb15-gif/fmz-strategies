"""WaveTrend extremes in the direction of the hourly close against an EMA 200 high / low channel, with an extreme /
channel stop and a 3 R target, 1-minute bars: when the last completed hour closed above the EMA 200 of highs, a bar
inside a WaveTrend oversold run (signal line <= -50 for more than one bar, or a WaveTrend cross up while oversold)
closing above EMA 12 goes long, stopped below the run's low (or the channel); shorts mirrored.
Port of FMZ strategy #490787 "多时段动态动量波动捕捉策略-Multi-Timeframe-Dynamic-Momentum-Wave-Capture-Strategy" (Enhanced Momentum Wave Catcher).

FMZ source id: 490787

Source
    https://www.fmz.com/strategy/490787 (PineScript v5, FMZ last modified 2025-04-16 14:53:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 186-269), EMA 12, EMA 200 of highs / lows, WaveTrend (hlc3, 9, 12, 3), -50 / 50, RR 3
    hourlyClose = request.security(ticker, "60", close); above = hourlyClose > EMA200(high) (below mirrored; kept)
    oversoldBars counts bars with wt2 <= -50, extremeLow = the lowest low of that run (na outside it)
    long = above and (oversoldBars > 1 or crossover(wt1, wt2)) and close > EMA 12, and longStop = min(extremeLow,
    EMA200(low) x 0.998) is not na -> entry long + exit(stop = longStop, limit = close + 3 x (close - longStop))

Interpretation choices (Pine rules in SURVEY_README.md)
    * request.security(..., "60", close) without lookahead is read as the last COMPLETED hour's close (house rule:
      higher bars only after they close), built from the port's minutes and taken from the first minute of the next
      hour (TradingView shows it on the hour's last minute: one minute earlier).
    * math.min with an na extremeLow is na, so an entry needs a live oversold (overbought) run, as written.
    * The bracket is placed with the entry from the signal bar: sl_stop = (close - longStop) / close, tp_stop = 3 x
      that, shifted one bar inside stops(), re-based on the fill. A later signal bar while in the trade re-places it
      (the entry itself is ignored): mark trailing_stop_pending; the port keeps the bracket of the entry.
    * The channel flags flip only on a close outside the channel, so a short can follow a long: entries reverse
      (REVERSAL INTENDED); a long and a short cannot fall on one bar.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the hourly close only after the hour completes.
    2 generic: PASS, oscillator levels, EMAs and price-relative stops.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-risk quantity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (hours are UTC clock hours of the minute data).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_490787_wavetrend_extreme_hourly_channel"
FAMILY = "wavetrend_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rr": [3.0, 1.5],
    "extreme_level": [50, 60],
}
DEFAULT_PARAMS = {"ema_fast": 12, "ema_slow_high": 200, "ema_slow_low": 200, "extreme_level": 50, "rr": 3.0,
                  "confirmation_bars": 1}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _last_completed_hour_close(bars_df):
    """Close of the last bar of the previous clock hour, for each bar (na in the first hour)."""
    hour = bars_df.index.floor("h")
    c = bars_df["close"].to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    cur_h, prev_close, last_close = None, np.nan, np.nan
    for i in range(len(c)):
        if hour[i] != cur_h:
            prev_close = last_close if cur_h is not None else np.nan
            cur_h = hour[i]
        out[i] = prev_close
        last_close = c[i]
    return out


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean().to_numpy()
    eh = h.ewm(span=int(p["ema_slow_high"]), adjust=False).mean().to_numpy()
    el = lo.ewm(span=int(p["ema_slow_low"]), adjust=False).mean().to_numpy()
    src = (h + lo + c) / 3
    esa = src.ewm(span=9, adjust=False).mean()
    de = (src - esa).abs().ewm(span=9, adjust=False).mean()
    wt1 = ((src - esa) / (0.015 * de)).ewm(span=12, adjust=False).mean()
    wt2 = wt1.rolling(3).mean()
    x_up = ((wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))).to_numpy()
    x_dn = ((wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))).to_numpy()
    w2 = wt2.to_numpy(dtype=float)
    hc = _last_completed_hour_close(bars_df)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lvl, conf, rr = float(p["extreme_level"]), int(p["confirmation_bars"]), float(p["rr"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dsl = np.full(m, np.nan)
    os_n = ob_n = 0
    x_lo = x_hi = np.nan
    above = below = False
    for i in range(m):
        if w2[i] <= -lvl:
            os_n += 1
            x_lo = lv[i] if np.isnan(x_lo) else min(lv[i], x_lo)
        else:
            os_n, x_lo = 0, np.nan
        if w2[i] >= lvl:
            ob_n += 1
            x_hi = hv[i] if np.isnan(x_hi) else max(hv[i], x_hi)
        else:
            ob_n, x_hi = 0, np.nan
        if hc[i] > eh[i]:
            above, below = True, False
        elif hc[i] < el[i]:
            above, below = False, True
        if above and (os_n > conf or x_up[i]) and cv[i] > ef[i] and not np.isnan(x_lo):
            stop = min(x_lo, el[i] * 0.998)
            d = (cv[i] - stop) / cv[i]
            if d > 0:
                le[i], dsl[i] = True, d
        if below and (ob_n > conf or x_dn[i]) and cv[i] < ef[i] and not np.isnan(x_hi):
            stop = max(x_hi, eh[i] * 1.002)
            d = (stop - cv[i]) / cv[i]
            if d > 0:
                se[i], dsl[i] = True, d
    return le, se, dsl, rr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _run(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dsl, rr = _run(bars_df, p)
    d = pd.Series(dsl, index=bars_df.index)
    return {"sl_stop": d.shift(1), "tp_stop": (rr * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
