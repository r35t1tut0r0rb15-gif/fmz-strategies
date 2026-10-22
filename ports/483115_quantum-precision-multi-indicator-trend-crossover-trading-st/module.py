"""EMA 10 / 30 crossings with a confirmation (momentum 10 up, 20-bar standard deviation over its SMA 50, EMA 20 over EMA 50), hourly bars: a confirmed up-cross goes long, an unconfirmed down-cross goes short, each with a 2 ATR 14 stop and a 6 ATR target from the signal close; reversing.
Port of FMZ strategy #483115 "Quantum Precision Multi Indicator Trend Crossover Trading Strategy" (Quantum Precision Forex Strategy).

FMZ source id: 483115

Source
    https://www.fmz.com/strategy/483115 (PineScript v5, FMZ last modified 2025-02-21 14:13:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-145), ATR 14 x 2; RR 3; confirmation 10; 10 % of equity
    confirm = mom(close, 10) > 0 and stdev(close, 20) > sma(stdev(close, 20), 50) and ema20 > ema50
    confirm and crossover(ema10, ema30) -> entry Long + exit(stop = close - 2 atr, limit = close + 6 atr);  not confirm and crossunder(ema10, ema30) -> entry Short + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trendlines and the correlation "sentiment" are plots only. The levels are fixed at the signal
      close and sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256). The crossings alternate, so a side never re-sends its bracket while held. An
      entry on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4).
      The 10 % of equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with momentum / volatility / trend confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483115_ema10_30_cross_mom_vol_trend_confirm_atr2_rr3_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_multiplier": [2.0, 1.5],
    "risk_reward_ratio": [3.0, 2.0],
}
DEFAULT_PARAMS = {"atr_multiplier": 2.0, "risk_reward_ratio": 3.0, "atr_length": 14, "confirmation_length": 10}


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


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def ema(x, n):
        return x.ewm(span=n, adjust=False).mean()

    sd20 = c.rolling(20).std(ddof=0)
    conf = (c - c.shift(int(p["confirmation_length"])) > 0) & (sd20 > sd20.rolling(50).mean()) & \
        (ema(c, 20) > ema(c, 50))
    e10, e30 = ema(c, 10), ema(c, 30)
    le = conf & (e10 > e30) & (e10.shift(1) <= e30.shift(1))
    se = ~conf & (e10 < e30) & (e10.shift(1) >= e30.shift(1))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    a = _rma(tr, int(p["atr_length"])) * float(p["atr_multiplier"])
    b = a * float(p["risk_reward_ratio"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
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
