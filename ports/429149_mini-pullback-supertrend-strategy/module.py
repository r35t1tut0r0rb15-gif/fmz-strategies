"""SuperTrend flip with EMA, RSI, MACD and stochastic-RSI pullback filters, long only, hourly bars: a flip to
up-trend with EMA 21 > 50 > 200, RSI >= 50, a MACD histogram not weakening and a recent stoch-RSI cross out of
oversold goes long, with a 1.5 ATR stop and a 3 ATR target.
Port of FMZ strategy #429149 "Mini Pullback Supertrend Strategy" (pullb).

FMZ source id: 429149

Source
    https://www.fmz.com/strategy/429149 (PineScript v5, FMZ last modified 2023-10-13 15:49:29).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 160-266), SuperTrend 14 / 2 on close, EMA 21 / 50 / 200, MACD 12 / 26 / 9, RSI 14, stoch-RSI 14 / 14 / 3 / 3, 5 bars back
    buy = flip up and rsi >= 50 and (hist >= 0 or hist < hist[1]) and ema21 > ema50 > ema200
          and a K-over-D cross from below 20 within the last 6 bars and not (K > 80 and D > 80)
    buy -> entry long + exit(stop = close - 1.5 atr(14), limit = close + 3 atr(14))

Interpretation choices (Pine rules in SURVEY_README.md)
    * SuperTrend as the source's own lines (source close, Wilder ATR 14 x 2; bands ratcheted on
      close[1]). The stoch-RSI loop counts K[i] > D[i] and K[i+1] < D[i+1] with both under 20, i = 0..5.
    * The bracket is fixed at entry from the signal bar (sl_atr / tp_atr x ATR(14), shifted one bar
      inside stops(), re-based on the fill). A later buy signal while long re-places the exit from that
      bar's close (same id): the moved levels are not expressible (rule 2): pending, mark
      trailing_stop_pending.
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-placement pending).
    2 generic: PASS, ATR multiples and oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_429149_supertrend_pullback_filters"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "multiplier": [2.0, 3.0],
    "look_for": [5, 3],
}
DEFAULT_PARAMS = {"periods": 14, "multiplier": 2.0, "look_for": 5, "sl_atr": 1.5, "tp_atr": 3.0, "atr_length": 14}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e = lambda x, n: x.ewm(span=int(n), adjust=False).mean()  # noqa: E731
    atr = _atr(bars_df, int(p["periods"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    trend = np.ones(m, dtype=np.int8)
    for i in range(m):
        ur, dr = cv[i] - p["multiplier"] * atr[i], cv[i] + p["multiplier"] * atr[i]
        u1 = up[i - 1] if i >= 1 and not np.isnan(up[i - 1]) else ur
        d1 = dn[i - 1] if i >= 1 and not np.isnan(dn[i - 1]) else dr
        up[i] = max(ur, u1) if i >= 1 and cv[i - 1] > u1 else ur
        dn[i] = min(dr, d1) if i >= 1 and cv[i - 1] < d1 else dr
        t = trend[i - 1] if i >= 1 else 1
        if t == -1 and cv[i] > d1:
            t = 1
        elif t == 1 and cv[i] < u1:
            t = -1
        trend[i] = t
    flip_up = pd.Series((trend == 1) & (np.concatenate(([1], trend[:-1])) == -1), index=c.index)
    macd = e(c, 12) - e(c, 26)
    hist = macd - e(macd, 9)
    rsi = _rsi(c, 14)
    r1 = _rsi(c, 14)
    ll, hh = r1.rolling(14).min(), r1.rolling(14).max()
    k = (100 * (r1 - ll) / (hh - ll).replace(0.0, np.nan)).rolling(3).mean()
    d = k.rolling(3).mean()
    x = (k > d) & (k.shift(1) < d.shift(1)) & (k.shift(1) < 20) & (d.shift(1) < 20)
    count = sum(x.shift(i, fill_value=False).astype(int) for i in range(int(p["look_for"]) + 1))
    stoch_ok = (count > 0) & ~((k > 80) & (d > 80))
    ema_ok = (e(c, 21) > e(c, 50)) & (e(c, 50) > e(c, 200))
    long_e = (flip_up & (rsi >= 50) & ((hist >= 0) | (hist < hist.shift(1))) & ema_ok & stoch_ok).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
