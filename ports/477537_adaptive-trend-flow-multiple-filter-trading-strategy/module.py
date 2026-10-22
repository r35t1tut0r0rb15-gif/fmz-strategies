"""Adaptive trend-flow flips (EMA 2 / 4 basis of hlc3 with an EMA-2-smoothed stdev band x 2), 45-minute bars, long only: a flip up with the close above its SMA 4 and MACD (2 / 7 / 2) over its signal buys, a flip down closes.
Port of FMZ strategy #477537 "Adaptive Trend Flow Multiple Filter Trading Strategy" (Adaptive Trend Flow Strategy with Filters for SPX).

FMZ source id: 477537

Source
    https://www.fmz.com/strategy/477537 (PineScript v6, FMZ last modified 2025-01-06 11:58:25).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 87-202), length 2, smoothing 2, sensitivity 2.0; SMA filter 4; MACD filter 2 / 7 / 2; leverage 4.5 x equity / close as qty; capital 1000, margin 20 %, commission 0.01 per order, slippage 2
    basis = (ema(hlc3, 2) + ema(hlc3, 4)) / 2;  band = ema(stdev(hlc3, 2), 2) x 2;  trend: na level -> close > basis ? 1 : -1;  1 and close < lower -> -1;  -1 and close > upper -> 1
    trend flips to 1 and close > sma(close, 4) and macd > signal -> entry Long (qty = equity / close x 4.5);  trend flips to -1 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trend state starts on the first bar where its level exists and then flips on closes beyond the
      opposite band, as written (a loop). The filters apply to the long entry only. The automation
      inputs (account id, key, ticker) and alerts are not ported. Long only. The leveraged equity qty,
      capital and margin are sizing; the commission and slippage settings are costs and are not ported
      (house cost model). FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, adaptive band trend flips with SMA and MACD filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: leverage 4.5 x equity qty, capital 1000, margin 20 % stored, not ported; costs not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477537_adaptive_trend_flow_flip_sma_macd_filter_long"
FAMILY = "volatility_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [2, 10],
    "sensitivity": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 2, "sensitivity": 2.0, "smooth_len": 2, "sma_length": 4,
                  "macd_fast": 2, "macd_slow": 7, "macd_signal": 2}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    typ = (h + lo + c) / 3
    basis = (_ema(typ, n) + _ema(typ, 2 * n)) / 2
    vol = _ema(typ.rolling(n).std(ddof=0), p["smooth_len"])
    k = float(p["sensitivity"])
    up, dn = (basis + vol * k).to_numpy(), (basis - vol * k).to_numpy()
    bv, cv = basis.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    trend = np.zeros(m)
    tr, lvl = 0, np.nan
    for i in range(m):
        if np.isnan(lvl):
            tr = 1 if cv[i] > bv[i] else -1
            lvl = dn[i] if tr == 1 else up[i]
        if tr == 1:
            if cv[i] < dn[i]:
                tr, lvl = -1, up[i]
            else:
                lvl = dn[i]
        else:
            if cv[i] > up[i]:
                tr, lvl = 1, dn[i]
            else:
                lvl = up[i]
        trend[i] = tr
    t = pd.Series(trend, index=c.index)
    sma_ok = c > c.rolling(int(p["sma_length"])).mean()
    macd = _ema(c, p["macd_fast"]) - _ema(c, p["macd_slow"])
    macd_ok = macd > _ema(macd, p["macd_signal"])
    le = (t == 1) & (t.shift(1) == -1) & sma_ok & macd_ok
    lx = (t == -1) & (t.shift(1) == 1)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
