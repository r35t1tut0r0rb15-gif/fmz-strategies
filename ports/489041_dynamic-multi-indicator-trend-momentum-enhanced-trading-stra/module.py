"""EMA 20 / 50 up-crossings above the EMA 200 with RSI 14 over 55 and the MACD side, hourly bars, long only, with a 1.5 ATR 14 stop and a 2 R target from the signal close.
Port of FMZ strategy #489041 "Dynamic Multi Indicator Trend Momentum Enhanced Trading Strategy" (High-Win Trend & Momentum Strategy).

FMZ source id: 489041

Source
    https://www.fmz.com/strategy/489041 (PineScript v5, FMZ last modified 2025-04-01 14:41:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 160-207), EMA 20 / 50 / 200; RSI 14; MACD 12 / 26 / 9; ATR 14 x 1.5; RR 2; 10 % of equity
    crossover(ema20, ema50) and rsi > 55 and macd > signal and close > ema200 -> entry BUY + exit(stop = close - 1.5 atr, limit = close + 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The sell condition is only plotted. The bracket is set on the signal bar from its close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A later up-crossing while held re-sends the bracket; the port keeps the opening levels, mark
      trailing_stop_pending (as #434428). Long only. Stop module: portfolio_kwargs {} (driver D4). FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with trend / RSI / MACD filters and an ATR bracket.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_489041_ema20_50_cross_ema200_rsi55_macd_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_multiplier": [1.5, 2.5],
    "risk_reward_ratio": [2.0, 3.0],
}
DEFAULT_PARAMS = {"atr_multiplier": 1.5, "risk_reward_ratio": 2.0, "atr_length": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(n):
        return c.ewm(span=int(n), adjust=False).mean()

    f, s, t = ema(20), ema(50), ema(200)
    macd = ema(12) - ema(26)
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (_rsi(c, 14) > 55) & (macd > sig) & (c > t)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atr_length"])) * float(p["atr_multiplier"])
    return le, c - a, c + a * float(p["risk_reward_ratio"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl, tp = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    thr = lf & ((sl.shift(1) >= o) | (tp.shift(1) <= o))    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl, tp = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - sl.shift(1) / o
    tp_f = tp.shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
