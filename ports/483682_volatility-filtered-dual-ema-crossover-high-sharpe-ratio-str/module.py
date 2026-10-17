"""EMA 10 / 30 crosses taken only when ATR 14 is more than one standard deviation above its 20-bar mean, with a
2 ATR stop / 4 ATR target, 1-minute bars: EMA 10 crossing above EMA 30 with ATR > SMA(ATR, 20) + stdev(ATR, 20) goes
long; the mirror goes short.
Port of FMZ strategy #483682 "波动率过滤双均线交叉高夏普比策略-Volatility-Filtered-Dual-EMA-Crossover-High-Sharpe-Ratio-Strategy" (Aggressive Strategy for High IV Market).

FMZ source id: 483682

Source
    https://www.fmz.com/strategy/483682 (PineScript v6, FMZ last modified 2025-02-25 11:23:13).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 158-196), EMA 10 / 30, ATR 14, ATR mean / stdev 20
    long = crossover(ema10, ema30) and atr > sma(atr, 20) + stdev(atr, 20) (short mirrored)
    exit(stop = close -+ 2 ATR, limit = close +- 4 ATR), re-issued every bar for each entry id

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits are re-issued on every bar from the CURRENT close and ATR (a moving level): fixed at the entry
      (sl_stop = sl_mult x ATR / close, tp_stop = tp_mult x ATR / close of the signal bar, shifted one bar inside
      stops() and re-based on the fill), mark trailing_stop_pending (desktop convention).
    * The risk-based qty (1 % of equity over 2 ATR) is sizing: not ported. The slippage input is unused.
    * ta.stdev is the population standard deviation (ddof 0).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, moving averages and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based qty is quoted in original_sizing.txt and not ported; the bracket via stops().
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

NAME = "fmz_483682_ema10_30_cross_atr_spike_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 1.5],
    "tp_mult": [4.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 10, "slow": 30, "atr_len": 14, "atr_mean_len": 20, "atr_std_len": 20,
                  "sl_mult": 2.0, "tp_mult": 4.0}


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
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    atr = _atr(bars_df, int(p["atr_len"]))
    hot = atr > atr.rolling(int(p["atr_mean_len"])).mean() + atr.rolling(int(p["atr_std_len"])).std(ddof=0)
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & hot).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & hot).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
