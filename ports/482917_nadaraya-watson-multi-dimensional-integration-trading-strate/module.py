"""A weighted sum of four Gaussian-smoothed series (close, RSI 14 / 100, ATR 14 / close, distance from the SMA 50) crossing its SMA 10, with an SMA 200 side and RSI 14 over / under 50, 1-minute bars: the up-cross goes long and the down-cross goes short, each with a 1.5 % stop and a 3 % target from the fill; reversing.
Port of FMZ strategy #482917 "基于Nadaraya-Watson的多维度整合交易策略-Multi-Dimensional-Integration-Trading-Strategy-Based-on-Nadaraya-Watson" (Enhanced Multidimensional Integration Strategy with Nadaraya).

FMZ source id: 482917

Source
    https://www.fmz.com/strategy/482917 (PineScript v5, FMZ last modified 2025-02-27 17:21:26).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-213), weights 0.4 / 0.2 / 0.2 / 0.2; smoothing 20 bars, bandwidth 20; SMA 10 of the sum; SMA 200; RSI 14 / 50; stop 1.5 %; target 3 %; 10 % of equity, capital 10000
    nadaraya_smooth(src, 20, 20) = sum(w_i x src[i]) / sum(w_i), w_i = exp(-0.5 ((20 - 1 - i) / 20)^2), i = 0..19, na before bar 20
    crossover(integrated, sma(integrated, 10)) and close > sma200 and rsi > 50 -> entry Long;  crossunder and close < sma200 and rsi < 50 -> entry Short
    position long -> exit(stop = avg x 0.985, limit = avg x 1.03);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The kernel weights grow with the lag (the oldest of the 20 bars weighs most), as written; it uses
      only the current and past bars. The bracket is sent from the fill bar's close around the average
      price; it is ported as fixed fractions of the fill, active from the fill bar (as #440797). An entry
      on the other side reverses (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (driver D4). The
      10 % of equity size and the capital are sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, smoothed composite crossing its SMA with trend / RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and capital stored, not ported.
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

NAME = "fmz_482917_nw_composite_sma10_cross_sma200_rsi50_pct_bracket_reversal"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "smooth_length": [20, 10],
    "take_profit_perc": [3.0, 2.0],
}
DEFAULT_PARAMS = {"smooth_length": 20, "take_profit_perc": 3.0, "bandwidth": 20.0, "stop_loss_perc": 1.5,
                  "w_technical": 0.4, "w_emotional": 0.2, "w_extrasensor": 0.2, "w_intentional": 0.2,
                  "trend_length": 200, "rsi_level": 50}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def _nw(x, n, bw):
    """sum(w_i x[t - i]) / sum(w_i), w_i = exp(-0.5 ((n - 1 - i) / bw)^2), na before bar n."""
    lag = np.arange(n, dtype=float)
    w = np.exp(-0.5 * ((n - 1 - lag) / bw) ** 2)
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m > n:
        out[n - 1:] = np.convolve(v, w, mode="full")[n - 1:m] / w.sum()
        out[n - 1] = np.nan                  # bar_index < n is na
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n, bw = int(p["smooth_length"]), float(p["bandwidth"])
    r = _rsi(c, 14)
    dims = [(c, p["w_technical"]), (r / 100, p["w_emotional"]), (_atr(bars_df, 14) / c, p["w_extrasensor"]),
            ((c - c.rolling(50).mean()) / c, p["w_intentional"])]
    sig = sum(float(w) * _nw(x, n, bw) for x, w in dims)
    ref = sig.rolling(10).mean()
    tr = c.rolling(int(p["trend_length"])).mean()
    lvl = float(p["rsi_level"])
    le = (sig > ref) & (sig.shift(1) <= ref.shift(1)) & (c > tr) & (r > lvl)
    se = (sig < ref) & (sig.shift(1) >= ref.shift(1)) & (c < tr) & (r < lvl)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    sl = pd.Series(float(p["stop_loss_perc"]) / 100, index=idx).shift(1)
    tp = pd.Series(float(p["take_profit_perc"]) / 100, index=idx).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
