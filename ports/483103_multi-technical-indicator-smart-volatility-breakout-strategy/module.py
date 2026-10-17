"""Closes below the lower Bollinger band with a stochastic %K / %D cross up below 20 on an ATR spike, long only, with a
1.5 ATR stop / 1.5 ATR target, 1-minute bars: close < lower BB(20, 2), %K crossing above %D with %K < 20 and ATR(14)
above 1.5 x its 14-bar mean goes long; the mirror at the upper band closes it.
Port of FMZ strategy #483103 "多重技术指标智能波动突破策略-Multi-Technical-Indicator-Smart-Volatility-Breakout-Strategy" (Bollinger Bands + Stochastic Oscillator + ATR Strategy).

FMZ source id: 483103

Source
    https://www.fmz.com/strategy/483103 (PineScript v5, FMZ last modified 2025-02-21 13:42:44).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 122-191), BB 20 x 2, stochastic 14 / 3 / 3, ATR 14, ATR mult 1.5
    buy = close < lower and crossover(k, d) and k < 20 and atr > sma(atr, 14) x 1.5 -> entry long +
    exit(stop = close - 1.5 ATR, limit = close + 1.5 ATR)
    sell = close > upper and crossunder(k, d) and k > 80 and atr > sma(atr, 14) x 1.5 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed with the entry from the signal bar: atr_mult x ATR / close both ways, shifted one bar inside
      stops() and re-based on the fill (house rule). A buy signal while held re-places it: mark trailing_stop_pending;
      the port keeps the entry's bracket. atr_mult is one input for the ATR threshold and the bracket, as written.
    * ta.stdev is the population standard deviation. Long only; the sell close is an exit signal.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, Bollinger bands, a stochastic and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483103_bb_stoch_atr_spike_long_bracket"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 1.0],
    "bb_mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "k_len": 14, "k_smooth": 3, "d_smooth": 3, "atr_len": 14,
                  "atr_mult": 1.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    kn = int(p["k_len"])
    ll, hh = lo.rolling(kn).min(), h.rolling(kn).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    d = k.rolling(int(p["d_smooth"])).mean()
    atr = _atr(bars_df, int(p["atr_len"]))
    hot = atr > atr.rolling(int(p["atr_len"])).mean() * p["atr_mult"]
    buy = ((c < basis - dev) & (k > d) & (k.shift(1) <= d.shift(1)) & (k < 20) & hot).astype(bool)
    sell = ((c > basis + dev) & (k < d) & (k.shift(1) >= d.shift(1)) & (k > 80) & hot & ~buy).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, sell, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": a, "tp_stop": a}


def portfolio_kwargs(**params):
    return {}
