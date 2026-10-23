"""2-hour bars, long only: the EMA 21 crossing over the EMA 55 with RSI 14 more than 10 above its EMA 14, the close above the supertrend (3, 14) and the EMA 200, volume over 1.5 x its EMA 20 and ATR 14 above its EMA 48, at least 6 hours after the previous entry signal, goes long; an EMA crossing under, RSI crossing under its EMA - 15, or the close crossing under 0.98 x the supertrend closes it.
Port of FMZ strategy #482465 "Hybrid EMA Momentum Trading System with Trend Persistence Analysis Strategy" (Hybrid Trend Momentum Strategy by Biege ver. 1.0).

FMZ source id: 482465

Source
    https://www.fmz.com/strategy/482465 (PineScript v6, FMZ last modified 2025-02-18 15:27:29).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 100-156), EMA 21 / 55 / 200; RSI 14 and EMA 14; supertrend 3 / 14; volume EMA 20 x 1.5; ATR 14 vs EMA 48; cooldown 360 minutes
    entryCondition = crossover(ema21, ema55) and rsi > ema(rsi, 14) + 10 and close > supertrend and close > ema200 and volume > ema(volume, 20) x 1.5 and atr > ema(atr, 48) and (na(lastTradeTime) or time - lastTradeTime >= 360 min) -> entry Buy, lastTradeTime := time
    exitCondition = crossunder(ema21, ema55) or crossunder(rsi, rsiEMA - 15) or crossunder(close, supertrend x 0.98) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cooldown runs from the open time of the last entry-signal bar (also a signal while long, which
      adds nothing), measured on the bar timestamps. Each exit test is the opposite of an entry test, so
      an entry and a close never meet on one bar. ta.supertrend as Pine's reference implementation. Long
      only. No sizing code. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, filtered EMA crossings with supertrend / RSI / volume / volatility confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its EMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482465_ema21_55_cross_supertrend_rsi_volume_atr_cooldown_2h_long_only"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cooldown_min": [360, 720],
    "vol_mult": [1.5, 1.0],
}
DEFAULT_PARAMS = {"cooldown_min": 360, "vol_mult": 1.5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f, s, t = (c.ewm(span=n, adjust=False).mean() for n in (21, 55, 200))
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    r = _rsi(c, 14)
    re = r.ewm(span=14, adjust=False).mean()
    st, _ = _supertrend(bars_df, 3.0, 14)
    raw = (_xo(f, s) & (r > re + 10) & (c > st) & (c > t)
           & (v > v.ewm(span=20, adjust=False).mean() * float(p["vol_mult"]))
           & (atr > atr.ewm(span=48, adjust=False).mean())).to_numpy()
    ex = (_xo(s, f) | _xo(re - 15, r) | _xo(st * 0.98, c)).to_numpy()
    tm = bars_df.index.asi8 // 10**6                     # bar open times in ms, as Pine's time
    cool = int(p["cooldown_min"]) * 60 * 1000
    m = len(raw)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last, pos = None, 0
    for i in range(m):
        if raw[i] and (last is None or tm[i] - last >= cool):
            last = tm[i]
            if pos == 0:
                le[i], pos = True, 1
        elif pos == 1 and ex[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
