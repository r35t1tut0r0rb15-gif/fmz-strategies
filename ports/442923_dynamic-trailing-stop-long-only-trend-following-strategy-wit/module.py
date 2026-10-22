"""ADX(14, 14) crossing over 27 with +DI above -DI, 1-hour bars, long only: from flat the crossing goes long with a stop 5.5 ATR(14) under the signal close; the script ratchets that stop up with each
close, a move the port keeps pending.
Port of FMZ strategy #442923 "Dynamic Trailing Stop Long Only Trend Following Strategy with Seasonality Filter" (MBV-SP500-CLIMBER (DMI Strategy with ADX and ATR-based Trailing SL)).

FMZ source id: 442923

Source
    https://www.fmz.com/strategy/442923 (PineScript v5, FMZ last modified 2024-02-27 14:01:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-256), DI 14, ADX smoothing 14, threshold 27; ATR 14 x 5.5; trading time (true); seasonality off; all weekdays on
    longSignal = crossover(adx, 27) and plus > minus;  flat -> entry Long, SL = close - 5.5 atr;  in position: SL = max(SL, close - 5.5 atr);  exit(stop = SL) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop starts at the signal close less 5.5 ATR: sl_stop = 5.5 ATR / close of the signal bar,
      shifted one bar inside stops() and re-based on the fill. The script then raises it to each bar's
      close less 5.5 of that bar's ATR, a ratchet the house trails cannot express (the house volatility
      trail anchors on the best price and may retreat): the later moves are not followed, mark
      trailing_stop_pending (as #440292). The trading-time test returns true and seasonality is off.
      ta.dmi follows the script's own rma smoothing with fixnan. Long only. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ratchet pending.
    2 generic: PASS, ADX threshold crossing with DI direction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the trading-time test returns true).
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442923_adx27_cross_di_atr_stop_long"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_threshold": [27.0, 20.0],
    "atr_mult": [5.5, 3.0],
}
DEFAULT_PARAMS = {"adx_threshold": 27.0, "atr_mult": 5.5, "di_len": 14, "adx_len": 14, "atr_len": 14}


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


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def _fraction(bars_df, p):
    return float(p["atr_mult"]) * _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo = bars_df["high"], bars_df["low"]
    up, down = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > down) & (up > 0), up, 0.0))
    mdm = down.where(down.isna(), np.where((down > up) & (down > 0), down, 0.0))
    n = int(p["di_len"])
    trur = _rma(_tr(bars_df), n)
    plus = _fixnan(100 * _rma(pdm, n) / trur)
    minus = _fixnan(100 * _rma(mdm, n) / trur)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), int(p["adx_len"]))
    th = float(p["adx_threshold"])
    go = ((adx > th) & (adx.shift(1) <= th) & (plus > minus)).to_numpy()
    sl = _fraction(bars_df, p).to_numpy()
    ov, lv = bars_df["open"].to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ov[entry_i] * (1 - s_):
            pos = 0
        if pos == 0 and go[i] and i + 1 < m and not np.isnan(sl[i]):
            le[i], pos, entry_i, s_ = True, 1, i + 1, sl[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _fraction(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
