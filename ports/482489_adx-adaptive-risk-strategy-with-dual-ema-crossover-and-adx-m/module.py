"""Closes crossing the EMA 50 in an EMA 50 / 200 trend with ADX 14 at 25 or more and the matching DI on top, 3-minute bars: each side enters with its stop half an ATR beyond the 5-bar low / high and a target 1.5 times that risk from the signal close; reversing.
Port of FMZ strategy #482489 "双均线趋势交叉结合ADX动量过滤的自适应风险策略-Adaptive-Risk-Strategy-with-Dual-EMA-Crossover-and-ADX-Momentum-Filter" (XAUUSD 15m Trend Strategy).

FMZ source id: 482489

Source
    https://www.fmz.com/strategy/482489 (PineScript v5, FMZ last modified 2025-02-18 16:21:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 86-135), EMA 50 / 200; DMI 14 / 14, ADX >= 25; swing lookback 5; ATR 14 x 0.5; risk-reward 1.5; margin 100 / 100
    ema50 > ema200 and adx >= 25 and di+ > di- and crossover(close, ema50) -> entry Long + exit(stop = lowest(low, 5) - 0.5 atr, limit = close + (close - stop) x 1.5);  mirror -> entry Short + exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while the side is
      held re-sends the bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      The margin settings are not sizing signals. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing / ATR bracket as fractions of the fill.
    2 generic: PASS, EMA pullback crossings in an ADX / DI trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 / 100 stored, not ported.
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

NAME = "fmz_482489_ema50_cross_ema200_adx25_di_swing5_atr_bracket_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25, 20],
    "risk_reward": [1.5, 2.5],
}
DEFAULT_PARAMS = {"adx_threshold": 25, "risk_reward": 1.5, "ema_fast": 50, "ema_slow": 200, "lookback": 5,
                  "dmi_length": 14, "atr_length": 14, "atr_buffer": 0.5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    plus, minus, adx = _dmi(bars_df, int(p["dmi_length"]))
    strong = adx >= float(p["adx_threshold"])
    le = (ef > es) & strong & (plus > minus) & (c > ef) & (c.shift(1) <= ef.shift(1))
    se = (ef < es) & strong & (minus > plus) & (c < ef) & (c.shift(1) >= ef.shift(1))
    a = _atr(bars_df, int(p["atr_length"])) * float(p["atr_buffer"])
    n = int(p["lookback"])
    l_sl, s_sl = lo.rolling(n).min() - a, h.rolling(n).max() + a
    rr = float(p["risk_reward"])
    lvl = {"l_sl": l_sl, "l_tp": c + (c - l_sl) * rr, "s_sl": s_sl, "s_tp": c - (s_sl - c) * rr}
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
