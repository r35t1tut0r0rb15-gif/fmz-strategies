"""Closes under the lower Bollinger 20 / 2 band with a Stochastic 14 / 3 / 3 up-cross under 20 while ATR 14 exceeds 1.5 x its SMA, 1-minute bars, long only: the signal goes long with a 1.5 ATR stop and target from the signal close; the mirror above the upper band closes.
Port of FMZ strategy #483103 "Multi Technical Indicator Smart Volatility Breakout Strategy" (Bollinger Bands + Stochastic Oscillator + ATR Strategy).

FMZ source id: 483103

Source
    https://www.fmz.com/strategy/483103 (PineScript v5, FMZ last modified 2025-02-21 13:42:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-192), Bollinger 20 x 2; Stochastic 14 / 3 / 3; ATR 14, threshold 1.5 x SMA 14 of ATR; bracket 1.5 ATR; 10 % of equity
    close < lower and crossover(k, d) and k < 20 and atr > 1.5 sma(atr, 14) -> entry Long + exit(stop = close - 1.5 atr, limit = close + 1.5 atr)
    close > upper and crossunder(k, d) and k > 80 and atr > threshold -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed at the signal close and sent as fractions of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256). A repeat signal while held re-sends
      the bracket; stops() keeps the first, so the repeat case is marked trailing_stop_pending (as
      #434428). Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4).
      The 10 % of equity size is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, band / Stochastic reversals in high volatility.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483103_bb20_lower_stoch_cross_atr_spike_atr1_5_bracket_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 1.2],
    "bb_length": [20, 40],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "bb_length": 20, "bb_mult": 2.0, "stoch_length": 14, "k_smooth": 3,
                  "d_smooth": 3, "atr_length": 14}


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
    n = int(p["bb_length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = basis + float(p["bb_mult"]) * sd, basis - float(p["bb_mult"]) * sd
    sl_ = int(p["stoch_length"])
    rng = h.rolling(sl_).max() - lo.rolling(sl_).min()
    k = (100 * (c - lo.rolling(sl_).min()) / rng.where(rng > 0)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    al = int(p["atr_length"])
    atr = _rma(tr, al)
    km = float(p["atr_mult"])
    hot = atr > atr.rolling(al).mean() * km
    le = (c < dn) & (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20) & hot
    lx = (c > up) & (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80) & hot
    return le, lx, {"l_sl": c - km * atr, "l_tp": c + km * atr}


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, (lx | (lf & l_thr)) & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - lvl["l_sl"].shift(1) / o
    tp_f = lvl["l_tp"].shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
