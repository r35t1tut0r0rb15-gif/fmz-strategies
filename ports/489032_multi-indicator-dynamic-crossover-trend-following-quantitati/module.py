"""SMA 5 / 20 crosses with RSI and Bollinger filters and a 2 / 4 ATR bracket, 3-minute bars: SMA 5 crossing above SMA
20 with RSI 14 below 70 and the close below the upper band goes long (closing a short); the mirror goes short; each
trade has a stop 2 ATR and a target 4 ATR from the signal bar's close.
Port of FMZ strategy #489032 "多指标动态交叉趋势跟踪量化策略分析-Multi-Indicator-Dynamic-Crossover-Trend-Following-Quantitative-Strategy-Analysis" (Crypto Futures Day Trading Strategy).

FMZ source id: 489032

Source
    https://www.fmz.com/strategy/489032 (PineScript v5, FMZ last modified 2025-04-01 13:30:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 193-244), SMA 5 / 20, RSI 14, BB 20 x 2, ATR 14 x 2 / 4
    long = crossover(sma5, sma20) and rsi < 70 and close < upperBB -> close short, entry long, levels close -+ 2 / 4 ATR
    short = crossunder and rsi > 30 and close > lowerBB -> mirrored
    in a position: exit(stop, limit) at the stored levels of the signal bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are stored on the signal bar and the exit re-issued with the same levels: a bracket fixed at the
      signal bar: sl_stop = 2 x ATR / close, tp_stop = 4 x ATR / close, shifted one bar inside stops(), re-based on the
      fill (house rule).
    * The close comes before the entry: a stop-and-reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {}
      (D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, SMAs, RSI, bands and ATR multiples.
    3 crypto-exchange-only: no ("Crypto Futures" in the title and the exchange pair only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489032_sma_5_20_cross_rsi_bb_atr_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 1.0],
    "tp_atr": [4.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 5, "slow": 20, "rsi_len": 14, "bb_len": 20, "bb_mult": 2.0, "atr_len": 14,
                  "sl_atr": 2.0, "tp_atr": 4.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi < 70) & (c < basis + dev)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi > 30) & (c > basis - dev)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
