"""MACD 12 / 26 / 9 signal crossings with EMA 200 side, ADX 14 over 20 and RSI on the 50 side, 3-hour bars: each side enters with a stop 1.5 ATR and a target 3 ATR from the signal close; reversing.
Port of FMZ strategy #482461 "Dynamic Wave Indicator Combination Strategy" (Optimized Impulse Wave Strategy).

FMZ source id: 482461

Source
    https://www.fmz.com/strategy/482461 (PineScript v5, FMZ last modified 2025-02-18 15:20:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-151), MACD 12 / 26 / 9; EMA 200; RSI 14; DMI 14 / 14, ADX > 20; ATR 14 x 1.5, risk-reward 2
    crossover(macd, signal) and close > ema200 and adx > 20 and rsi > 50 -> entry Long + exit(limit = close + 3 atr, stop = close - 1.5 atr);  mirror -> entry Short + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while the side is
      held re-sends the bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, MACD crossings with trend, ADX and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482461_macd_cross_ema200_adx20_rsi50_atr_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [20, 25],
    "risk_reward_ratio": [2, 3],
}
DEFAULT_PARAMS = {"adx_threshold": 20, "risk_reward_ratio": 2, "fast": 12, "slow": 26, "signal": 9,
                  "ema_length": 200, "rsi_length": 14, "adx_length": 14, "atr_length": 14, "atr_mult": 1.5}


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
    return 100 - 100 / (1 + up / dn)


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def _signals(bars_df, p):
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    sig = ema(macd, p["signal"])
    e200 = ema(c, p["ema_length"])
    r = _rsi(c, int(p["rsi_length"]))
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    strong = adx > float(p["adx_threshold"])
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (c > e200) & strong & (r > 50)
    se = (macd < sig) & (macd.shift(1) >= sig.shift(1)) & (c < e200) & strong & (r < 50)
    d = _atr(bars_df, int(p["atr_length"])) * float(p["atr_mult"])
    rr = float(p["risk_reward_ratio"])
    lvl = {"l_sl": c - d, "l_tp": c + d * rr, "s_sl": c + d, "s_tp": c - d * rr}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
