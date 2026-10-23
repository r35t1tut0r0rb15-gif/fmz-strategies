"""A MACD of an OBV shadow line (DEMA 9 of the OBV-pushed high / low minus EMA 26 of the close) with the source's 50-bar running-extreme "pivots", 30-minute bars: a confirmed top pivot of the line goes long, otherwise a bottom pivot goes short; reversing.
Port of FMZ strategy #366938 "OBV MACD Indicator" (OBV MACD Indicator).

FMZ source id: 366938

Source
    https://www.fmz.com/strategy/366938 (PineScript v4, FMZ last modified 2022-05-31 18:46:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 51-319), OBV shadow windows 28 / 14; OBV EMA 1; MA DEMA 9; MACD slow 26; slope length 2; pivot period 50
    v = cum(sign(change(close)) x volume);  shadow = (v - sma(v, 14)) / stdev(v - sma(v, 14), 28) x stdev(high - low, 28);  out = shadow > 0 ? high + shadow : low + shadow
    macd = dema(ema(out, 1), 9) - ema(close, 26);  tt1 = linear fit of the last 2 macd values at the current bar (= macd)
    max_upper = the running max of macd since the last 50-bar high (reset there);  pivoth = max_upper == max_upper[2] and max_upper[2] != max_upper[3] -> entry Long;  else pivotl (min mirror) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * tt1 resolves to the current MACD value (a two-point fit evaluated at its last point). The T-channel
      block and the close-based max / min feed only plots. The running min also resets to the line when the
      CLOSE is under it, as written (a price compared with an oscillator). highestbars / lowestbars take the
      most recent bar on a tie. The OBV cumulative sum only enters through its difference from its own SMA,
      so its start cancels; the first bar adds 0. A study() script sending strategy orders on FMZ; long on a
      top pivot and short on a bottom one, as written. REVERSAL INTENDED. No sizing code. FREQ = "30min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, OBV-shadow MACD running-extreme pivots.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the OBV increments sign(change) x volume; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_366938_obv_shadow_dema_macd_running_extreme_pivot_reversal"
FAMILY = "macd_momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len": [9, 21],
    "xbars": [50, 100],
}
DEFAULT_PARAMS = {"len": 9, "xbars": 50, "slow_length": 26, "window_len": 28, "v_len": 14}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _extreme_offset(x, n, side):
    """abs(highestbars / lowestbars(x, n)): bars back to the window's extreme (the most recent on a tie)."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)[:, ::-1]   # column 0 = current bar
        ok = ~np.isnan(win).all(axis=1)
        filled = np.where(np.isnan(win), -np.inf if side > 0 else np.inf, win)
        arg = filled.argmax(axis=1) if side > 0 else filled.argmin(axis=1)
        out[n - 1:] = np.where(ok, arg, np.nan)
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    w, vl = int(p["window_len"]), int(p["v_len"])
    dev = obv - obv.rolling(vl).mean()
    shadow = dev / dev.rolling(w).std(ddof=0) * (h - lo).rolling(w).std(ddof=0)
    out = (h + shadow).where(shadow > 0, lo + shadow)
    n = int(p["len"])
    e1 = out.ewm(span=n, adjust=False).mean()
    ma = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    macd = ma - c.ewm(span=int(p["slow_length"]), adjust=False).mean()
    xb = int(p["xbars"])
    hb, lb = _extreme_offset(macd, xb, 1), _extreme_offset(macd, xb, -1)
    mv, cv = macd.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(mv)
    mu, ml = np.full(m, np.nan), np.full(m, np.nan)
    mu_p = ml_p = np.nan
    for i in range(m):
        a = mv[i] if (hb[i] == 0 or np.isnan(mu_p)) else mu_p
        if mv[i] > a:
            a = mv[i]
        b = mv[i] if (lb[i] == 0 or np.isnan(ml_p)) else ml_p
        if cv[i] < b:
            b = mv[i]                                  # "if close < min_lower", as written
        if mv[i] < b:
            b = mv[i]
        mu[i], ml[i] = a, b
        mu_p, ml_p = a, b
    mus, mls = pd.Series(mu, index=c.index), pd.Series(ml, index=c.index)
    ph = (mus == mus.shift(2)) & (mus.shift(2) != mus.shift(3))
    pl = (mls == mls.shift(2)) & (mls.shift(2) != mls.shift(3))
    false = pd.Series(False, index=c.index)
    return ph, false, pl & ~ph, false.copy()


def portfolio_kwargs(**params):
    return {}
