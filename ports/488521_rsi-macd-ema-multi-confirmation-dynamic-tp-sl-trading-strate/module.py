"""Large engulfing candles or pin bars on the side of the EMA 50 with RSI 14 under 70 (over 30) and the MACD side, hourly bars: the bullish pattern goes long, the bearish goes short, each with a 1.5 ATR 14 stop and target from the signal close; reversing.
Port of FMZ strategy #488521 "多重确认动态止盈止损交易策略RSI与MACD结合EMA趋势和蜡烛形态识别-Multi-Confirmation-Dynamic-TP-SL-Trading-Strategy-RSI-and-MACD-Combined-with-EMA-Trend-and-Candlestick-Pattern-Recognition" (Enhanced Trading Strategy with RSI, MACD, TP/SL).

FMZ source id: 488521

Source
    https://www.fmz.com/strategy/488521 (PineScript v5, FMZ last modified 2025-03-28 15:37:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 186-252), EMA 50; RSI 14; MACD 12 / 26 / 9; engulfing body > 1.5 x previous and > SMA 5 of bodies; pin bar 0.66 / 0.33 / 2.5; ATR 14 x 1.5
    (bullish engulfing or bullish pin bar, close > ema50) and rsi < 70 and macd > signal -> entry BUY + exit(limit = close + 1.5 atr, stop = close - 1.5 atr);  mirror -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set on the signal bar from its close and sent as fractions of the fill open (a level
      at or through it is marketable and closed one bar late, as #458256). A later same-side signal while
      held re-sends the bracket; the port keeps the opening levels, mark trailing_stop_pending (as
      #434428). An entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, engulfing / pin-bar patterns with trend, RSI and MACD filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488521_engulf_pinbar_ema50_rsi_macd_atr15_bracket_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrMult": [1.5, 2.5],
    "emaLength": [50, 100],
}
DEFAULT_PARAMS = {"atrMult": 1.5, "emaLength": 50}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _signals(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    e = ema(c, p["emaLength"])
    r = _rsi(c, 14)
    macd = ema(c, 12) - ema(c, 26)
    sig = ema(macd, 9)
    body = (c - o).abs()
    pbody = body.shift(1)
    big = (body > pbody * 1.5) & (body > body.rolling(5).mean())
    o1, c1 = o.shift(1), c.shift(1)
    bull_eng = (c1 < o1) & (c > o) & (c > o1) & (o < c1) & big & (c > e)
    bear_eng = (c1 > o1) & (c < o) & (c < o1) & (o > c1) & big & (c < e)
    rng = h - lo
    up_sh = h - pd.concat([o, c], axis=1).max(axis=1)
    lo_sh = pd.concat([o, c], axis=1).min(axis=1) - lo
    bull_pin = (lo_sh > rng * 0.66) & (up_sh < rng * 0.33) & (lo_sh > body * 2.5) & (c > e)
    bear_pin = (up_sh > rng * 0.66) & (lo_sh < rng * 0.33) & (up_sh > body * 2.5) & (c < e)
    le = (bull_eng | bull_pin) & (r < 70) & (macd > sig)
    se = (bear_eng | bear_pin) & (r > 30) & (macd < sig)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, 14) * float(p["atrMult"])
    lvl = {"l_sl": c - a, "l_tp": c + a, "s_sl": c + a, "s_tp": c - a}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
