"""MACDouble and StochRSI, 1-minute bars: long when a fast and a slow MACD are both above their signal
lines, the bar's close + high beats the previous close + the high two bars back, and the StochRSI K is
above D under the buy trigger; the mirror goes short. A very wide stop (9000 ticks) guards positions.
Port of FMZ strategy #427613 "Dual MACD StochRSI Trading Strategy".

FMZ source id: 427613

Source
    https://www.fmz.com/strategy/427613 (PineScript v2, FMZ last modified 2023-09-22 16:55:55).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 205-267), MACD 10/21/9 and 31/63/30 (signal = SMA), StochRSI 3/3/11/11
    delta = MACD - sma(MACD, sig); delta2 on security(ticker, res, ...) with res = chart period (default)
    uptrend = (close + high) / (close[1] + high[2]); downtrend = (close + low) / (close[1] + low[2])
    long: delta > 0 and delta2 > 0 and uptrend > 1 and (k and d < 90) and k > d
    short: delta < 0 and delta2 < 0 and downtrend < 1 and (k and d > 20) and k < d
    strategy.exit("sell", loss = 9000) issued on short signals (no from_entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The custom-resolution switches default to the chart's period: both MACDs and the StochRSI are
      on the chart; the custom resolutions are not ported (their default 45 min is lower-timeframe
      free but off by default).
    * `(kRes and dRes < 90)` is ported as written: K is non-zero and not na, and D < 90 (v2 truthiness).
    * Criterion 2: the 9000-tick loss becomes `sl_atr` x Wilder ATR(14) of the signal bar (a fraction
      of its close, shifted one bar inside stops()); 900 USD on 1-minute BTC is about 30 ATR
      (judgement before any backtest). Pine's exit has no from_entry, so once issued it guards every
      later position; the port guards every position from the first (stated approximation: longs
      before the first short signal have no stop in Pine).
    * The year > 2012 window is dropped. Stop module: portfolio_kwargs {} (driver D4);
      REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: ADAPT, tick distance -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427613_macdouble_stochrsi"
FAMILY = "macd_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length_rsi": [11, 14],
    "buy_trig": [90, 80],
    "sl_atr": [30.0, 10.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 21, "sig": 9, "fast2": 31, "slow2": 63, "sig2": 30,
                  "smooth_k": 3, "smooth_d": 3, "length_rsi": 11, "length_stoch": 11,
                  "buy_trig": 90, "sell_trig": 20, "sl_atr": 30.0, "atr_length": 14}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    return 100 - 100 / (1 + up / dn)


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _delta(c, f, s, g):
    macd = c.ewm(span=f, adjust=False).mean() - c.ewm(span=s, adjust=False).mean()
    return macd - macd.rolling(g).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    d1 = _delta(c, int(p["fast"]), int(p["slow"]), int(p["sig"]))
    d2 = _delta(c, int(p["fast2"]), int(p["slow2"]), int(p["sig2"]))
    uptrend = (c + h) / (c.shift(1) + h.shift(2))
    downtrend = (c + lo) / (c.shift(1) + lo.shift(2))
    r = _rsi(c, int(p["length_rsi"]))
    ls = int(p["length_stoch"])
    rl, rh = r.rolling(ls).min(), r.rolling(ls).max()
    st = 100 * (r - rl) / (rh - rl)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    k_true = k.notna() & (k != 0)
    long_s = ((d1 > 0) & (d2 > 0) & (uptrend > 1) & k_true & (d < p["buy_trig"]) & (k > d)).to_numpy()
    short_s = ((d1 < 0) & (d2 < 0) & (downtrend < 1) & k_true & (d > p["sell_trig"]) & (k < d)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_s[i] and pos != 1:
            pos = 1
        elif short_s[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    pc = bars_df["close"].shift(1)
    tr = pd.concat([bars_df["high"] - bars_df["low"], (bars_df["high"] - pc).abs(),
                    (bars_df["low"] - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
