"""EMA 20 / 50 cross-ups in the EMA 200 trend with RSI and MACD confirmation and an ATR bracket, long only, hourly
bars: EMA 20 crossing above EMA 50 with RSI 14 above 55, the MACD above its signal and the close above EMA 200 goes
long, with a stop 1.5 ATR away and a target twice as far.
Port of FMZ strategy #489041 "动态多指标趋势动量优化交易策略-Dynamic-Multi-Indicator-Trend-Momentum-Enhanced-Trading-Strategy" (High-Win Trend & Momentum Strategy).

FMZ source id: 489041

Source
    https://www.fmz.com/strategy/489041 (PineScript v5, FMZ last modified 2025-04-01 14:41:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-195), EMA 20 / 50 / 200, RSI 14 > 55, MACD 12 / 26 / 9, ATR 14 x 1.5, RR 2
    buy = crossover(ema20, ema50) and rsi > 55 and macd > signal and close > ema200
    -> entry long + exit(stop = close - 1.5 ATR, limit = close + 2 x 1.5 ATR)   (the sell condition is never traded)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop = 1.5 x ATR / close, tp_stop = 2 x that, shifted one bar
      inside stops(), re-based on the fill (house rule).
    * Long only. Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs, oscillators and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489041_ema_cross_trend_rsi_macd_atr_bracket_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 3.0],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"ema_fast": 20, "ema_slow": 50, "ema_trend": 200, "atr_len": 14, "atr_mult": 1.5, "rr": 2.0}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    et = c.ewm(span=int(p["ema_trend"]), adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (_rsi(c, 14) > 55) & (macd > sig) & (c > et)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": (p["rr"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
