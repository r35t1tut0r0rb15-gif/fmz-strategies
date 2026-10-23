"""3-minute bars: an EMA 20 / 50 golden cross with the close above the upper Bollinger band and the SMA 200, a rising ADX, RSI under 70, MACD over its signal, stochastic %K over 20, CCI over -100, OBV over its EMA 20 and volume over twice its 20-bar average goes long with a 2 ATR stop and 4 ATR target; the mirror goes short; reversing.
Port of FMZ strategy #488137 "Multi Indicator Comprehensive Analysis Quantitative Trading Strategy Trend Momentum and Volatility Collaborative Prediction Model" (30 Gostergeli Strateji (BAKI REIS)).

FMZ source id: 488137

Source
    https://www.fmz.com/strategy/488137 (PineScript v5, FMZ last modified 2025-03-25 13:50:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 202-277), SMA 50 / 200; EMA 20 / 50; DMI 14 (ADX rising 3); RSI 14; MACD 12 / 26 / 9; stoch 14 / 3; CCI 20; BB 20 x 2; ATR 14; OBV EMA 20; volume SMA 20 x 2
    longCondition = rising(adx, 3) and rsi < 70 and macd > signal and stochK > 20 and cci > -100 and close > bbUpper and obv > ema(obv, 20) and volume > 2 x sma(volume, 20) and crossover(ema20, ema50) and close > sma200 -> entry Long, exit("Exit Long", stop = close - 2 atr, limit = close + 4 atr)
    shortCondition mirrored (falling ADX, rsi > 30, stochD < 80, cci < 100, close < bbLower, deathCross, close < sma200) -> entry Short, exit("Exit Short", stop = close + 2 atr, limit = close - 4 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits have no from_entry; each is taken to act on the trade its signal opens (as #471721's
      reading), as levels from the signal close: ported as fractions of the fill, exact (1e-6 floor).
      ta.rising(adx, 3) means the ADX above each of its 3 previous values. Most of the other indicators
      (SAR, supertrend, Williams %R, Keltner, Ichimoku, Chaikin, MFI, VWAP) only compute. REVERSAL
      INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, many-indicator agreement on golden / death crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV and against twice its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_488137_many_indicator_golden_cross_volume_atr_bracket_3m_reversal"
FAMILY = "trend_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "vol_mult": [2.0, 1.5],
    "tp_atr": [4.0, 3.0],
}
DEFAULT_PARAMS = {"vol_mult": 2.0, "sl_atr": 2.0, "tp_atr": 4.0}


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


def _adx(h, lo, c, n):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    return 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), n)


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = sliding_window_view(v, n)
        mean = win.mean(axis=1)
        mad = np.abs(win - mean[:, None]).mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n - 1:] = np.where(mad != 0, (v[n - 1:] - mean) / (0.015 * mad), np.nan)
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    s200 = c.rolling(200).mean()
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    adx = _adx(h, lo, c, 14)
    rising = (adx > adx.shift(1)) & (adx > adx.shift(2)) & (adx > adx.shift(3))
    falling = (adx < adx.shift(1)) & (adx < adx.shift(2)) & (adx < adx.shift(3))
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    ll, hh = lo.rolling(14).min(), h.rolling(14).max()
    k = (100 * (c - ll) / (hh - ll).where(hh != ll)).rolling(3).mean()
    d = k.rolling(3).mean()
    cci = _cci(c, 20)
    basis, dev = c.rolling(20).mean(), 2 * c.rolling(20).std(ddof=0)
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    obv_e = obv.ewm(span=20, adjust=False).mean()
    spike = v > float(p["vol_mult"]) * v.rolling(20).mean()
    golden = (e20 > e50) & (e20.shift(1) <= e50.shift(1))
    death = (e20 < e50) & (e20.shift(1) >= e50.shift(1))
    buy = (rising & (r < 70) & (macd > sig) & (k > 20) & (cci > -100) & (c > basis + dev) & (obv > obv_e)
           & spike & golden & (c > s200))
    sell = (falling & (r > 30) & (macd < sig) & (d < 80) & (cci < 100) & (c < basis - dev) & (obv < obv_e)
            & spike & death & (c < s200))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
