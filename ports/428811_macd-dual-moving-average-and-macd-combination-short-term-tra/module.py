"""EMA 50 interaction scalper with a bracket, hourly bars: price near the EMA 50 in the last 4 bars, the close on
the trend side, the stochastic(4) leaving its extreme, EMA 50 vs EMA 100 and the MACD histogram agreeing
gives the entry; each trade has a stop and a target.
Port of FMZ strategy #428811 "双重均线与MACD组合短线策略Dual-Moving-Average-and-MACD-Combination-Short-term-Trading-Strategy" (Forex scalper 2xEMA + SRSI + MACD).

FMZ source id: 428811

Source
    https://www.fmz.com/strategy/428811 (PineScript v4, FMZ last modified 2023-10-09 16:47:42).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 206-311), EMA 50 / 100, stochastic 4 smoothed 3, 20 / 80, MACD 12 / 26 / 10, TP / SL 200 ticks
    near = any crossover(close[k], ema50), k = 0..4; or cross(close[4], ema50) or crossunder(close[k], ema50), k = 0..3;
           or cross(low[k] or high[k], ema50), k = 1..4
    long: near and close > ema50 and crossover(K, 20) and ema50 > ema100 and hist >= 0 -> entry long
    short: near and close < ema50 and crossunder(K, 80) and ema50 < ema100 and hist <= 0 -> entry short
    exit(profit = 200, loss = 200, when = touch) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 200-tick target and stop become tp_atr / sl_atr x Wilder ATR(14) of the signal bar
      (shifted one bar inside stops(), re-based on the fill): 20 USD on hourly BTC is about 0.15 ATR
      (judgement before any backtest).
    * Stated approximation: the source places its bracket only on a bar where the price touched the
      EMA 50 in the previous 4 bars (`when = touch`), at the same distances from the entry; the port
      arms it from the entry.
    * crossover(close[k], ema50) compares the k-bars-old close with the current EMA (as written).
    * strategy.entry reverses. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (arming approximation stated).
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the bracket is ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG428811 (2 members, best partner #440083, Jaccard 0.941); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428811_ema50_scalper_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.15, 1.0],
    "sl_atr": [0.15, 1.0],
}
DEFAULT_PARAMS = {"ema_fast": 50, "ema_slow": 100, "stoch_len": 4, "smooth": 3, "oversold": 20, "overbought": 80,
                  "macd_fast": 12, "macd_slow": 26, "macd_signal": 10, "tp_atr": 0.15, "sl_atr": 0.15,
                  "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def _xu(a, b):
    return (a < b) & (a.shift(1) >= b.shift(1))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    e50, e100 = e(c, p["ema_fast"]), e(c, p["ema_slow"])
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["smooth"])).mean()
    macd = e(c, p["macd_fast"]) - e(c, p["macd_slow"])
    hist = macd - e(macd, p["macd_signal"])
    over = _xo(c, e50)
    for j in range(1, 5):
        over = over | _xo(c.shift(j), e50)
    under = _xo(c.shift(4), e50) | _xu(c.shift(4), e50)
    for j in range(0, 4):
        under = under | _xu(c.shift(j), e50)
    touch = pd.Series(False, index=bars_df.index)
    for j in range(1, 5):
        for s in (lo.shift(j), h.shift(j)):
            touch = touch | _xo(s, e50) | _xu(s, e50)
    near = over | under | touch
    long_e = (near & (c > e50) & _xo(k, pd.Series(float(p["oversold"]), index=c.index)) & (e50 > e100)
              & (hist >= 0)).astype(bool)
    short_e = (near & (c < e50) & _xu(k, pd.Series(float(p["overbought"]), index=c.index)) & (e50 < e100)
               & (hist <= 0) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / c
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
