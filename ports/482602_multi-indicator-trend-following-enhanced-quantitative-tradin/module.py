"""EMA 50 / 200 crossings with ADX 14 over 25 and an RSI 14 filter, 4-hour bars: the cross up with RSI over 30 goes long, the cross down with RSI under 70 goes short, each with a 5 % target and a 2 % stop from the signal close; RSI over 70 closes a long, under 30 a short; reversing.
Port of FMZ strategy #482602 "Multi Indicator Trend Following Enhanced Quantitative Trading Strategy" (Enhanced Trend Following Strategy).

FMZ source id: 482602

Source
    https://www.fmz.com/strategy/482602 (PineScript v5, FMZ last modified 2025-02-19 11:30:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-147), EMA 50 / 200; DMI 14 / 14, ADX > 25; RSI 14, 70 / 30; TP 5 %, SL 2 %; 200 % of equity
    crossover(ema50, ema200) and adx > 25 and rsi > 30 -> entry Long + exit(limit = close x 1.05, stop = close x 0.98);  mirror (rsi < 70) -> entry Short + exit(limit = close x 0.95, stop = close x 1.02)
    strategy.close("Long", when = rsi > 70);  strategy.close("Short", when = rsi < 30)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "240" EMAs are requested but feed no condition. The levels are fixed at the signal close and sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A filtered-out opposite crossing can leave a position held into a repeat crossing, which
      re-sends the bracket from the new close; stops() keeps the first, so the repeat case is marked
      trailing_stop_pending (as #434428), and an RSI close on that repeat bar is dropped. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark
      coarse_bar_stop. The 200 % of equity size is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with ADX and RSI filters and RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_482602_ema50_200_cross_adx25_rsi_pct_bracket_rsi_exit_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [25, 20],
    "rsi_overbought": [70, 80],
}
DEFAULT_PARAMS = {"adx_threshold": 25, "rsi_overbought": 70, "rsi_oversold": 30, "ema_fast": 50, "ema_slow": 200,
                  "adx_length": 14, "rsi_length": 14, "tp_frac": 0.05, "sl_frac": 0.02}


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
    f = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    r = _rsi(c, int(p["rsi_length"]))
    strong = adx > float(p["adx_threshold"])
    le = (f > s) & (f.shift(1) <= s.shift(1)) & strong & (r > float(p["rsi_oversold"]))
    se = (f < s) & (f.shift(1) >= s.shift(1)) & strong & (r < float(p["rsi_overbought"]))
    sl, tp = float(p["sl_frac"]), float(p["tp_frac"])
    lvl = {"l_sl": c * (1 - sl), "l_tp": c * (1 + tp), "s_sl": c * (1 + sl), "s_tp": c * (1 - tp)}
    return le, se, lvl, r


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl, r = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = (lf & l_thr) | (r > float(p["rsi_overbought"]))
    sx = (sf & s_thr) | (r < float(p["rsi_oversold"]))
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl, r = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
