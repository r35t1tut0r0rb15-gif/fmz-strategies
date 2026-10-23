"""Hourly bars: a supertrend (3.5, 8) up-trend with a positive MACD (10 / 21 / 7) histogram, ADX 18 over 28, a green bar on volume over 1.8 x its 20-bar average and no triple top divergence goes long; the mirror with a triple top divergence goes short; each trade gets a 2.2 ATR 14 stop from the signal close and closes when the supertrend turns; reversing.
Port of FMZ strategy #483101 "高级量化交易策略多维度指标融合的超级趋势ATR动态跟踪系统-Advanced-Quantitative-Trading-Strategy-Multi-Dimensional-Super-Trend-ATR-Dynamic-Tracking-System" (ETH Supertrend Enhanced Strategy (compact)).

FMZ source id: 483101

Source
    https://www.fmz.com/strategy/483101 (PineScript v6, FMZ last modified 2025-02-21 13:34:24).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 109-216), supertrend 3.5 / 8; MACD 10 / 21 / 7; DMI 18 / 18, ADX 28; volume SMA 20 x 1.8; RSI / MACD / volume 5-bar divergence; ATR 14 x 2.2
    longCondition = direction < 0 and hist > 0 and ADX > 28 and close > open and volValid and not tripleDivergence -> entry Long, stopPrice := close - 2.2 atr
    shortCondition = direction > 0 and hist < 0 and ADX > 28 and close < open and volValid and tripleDivergence -> entry Short, stopPrice := close + 2.2 atr
    every bar: exit("Exit Long", "Long", stop = stopPrice), exit("Exit Short", "Short", stop = stopPrice);  direction > 0 and long -> close Long;  direction < 0 and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stopPrice is set on signal bars only and re-sent every bar, so the stop is fixed at the signal:
      ported as a fraction of the fill, exact (1e-6 floor); the long set-up is a state and each repeat
      while long moves it to the new close (not followed: trailing_stop_pending). tripleDivergence = a
      high at the 5-bar high with RSI, the MACD histogram and volume all under their prior 5-bar highs.
      The supertrend closes are raw (a long's close bar has direction > 0, which no long entry has). The
      DMI outputs are named in the wrong order but only the ADX is used. REVERSAL INTENDED. 100 % of
      equity is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop at the signal close as a fraction of the fill.
    2 generic: PASS, supertrend trend entries with MACD / ADX / volume filters and a divergence switch.
    3 crypto-exchange-only: no (exchange pair in the header only (ETH named in the title)).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.8 x its SMA 20 and in the volume divergence; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483101_supertrend_macd_adx_volume_divergence_atr_stop_1h_reversal"
FAMILY = "supertrend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.5, 4.0],
    "stop_mult": [2.2, 3.0],
}
DEFAULT_PARAMS = {"factor": 3.5, "atr_len": 8, "adx_len": 18, "adx_min": 28.0, "vol_mult": 1.8, "stop_mult": 2.2}


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


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _st_dir(bars_df, factor, period):
    """Direction of ta.supertrend (Pine reference implementation), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, period).to_numpy()
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
    return pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    d = _st_dir(bars_df, float(p["factor"]), int(p["atr_len"]))
    macd = c.ewm(span=10, adjust=False).mean() - c.ewm(span=21, adjust=False).mean()
    hist = macd - macd.ewm(span=7, adjust=False).mean()
    n = int(p["adx_len"])
    _, _, adx = _dmi(h, lo, c, n, n)
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    r = _rsi(c, 14)
    at_high = h >= h.rolling(5).max().shift(1)
    div = (at_high & (r < r.rolling(5).max().shift(1)) & (hist < hist.rolling(5).max().shift(1))
           & (v < v.rolling(5).max().shift(1)))
    strong = adx > float(p["adx_min"])
    buy = (d < 0) & (hist > 0) & strong & (c > o) & vol_ok & ~div
    sell = (d > 0) & (hist < 0) & strong & (c < o) & vol_ok & div
    lx = (d > 0) & ~sell
    sx = (d < 0) & ~buy
    return buy.astype(bool), lx.astype(bool), sell.astype(bool), sx.astype(bool)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    dist = float(p["stop_mult"]) * _atr(bars_df, 14)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - dist).shift(1) / o)
            .mask(sf, (c + dist).shift(1) / o - 1))
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
