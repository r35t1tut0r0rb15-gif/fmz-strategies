"""MACD crosses with RSI on the far side of 40 / 59, with reversals and a 3 % close-based stop from the signal close,
1-minute bars: MACD crossing above its signal with RSI at or below 40 goes long; crossing below with RSI at or above 59
goes short; a long closes when a close falls 3 % below its signal close (a short mirrored).
Port of FMZ strategy #482891 "使用RSI和MACD双重过滤的动态止损趋势跟踪策略-Dynamic-Stop-Loss-Trend-Following-Strategy-with-RSI-and-MACD-Dual-Filtering" (EAG MACD + RSI Strategy).

FMZ source id: 482891

Source
    https://www.fmz.com/strategy/482891 (PineScript v5, FMZ last modified 2025-02-20 16:50:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-151), RSI 14 (59 / 40), MACD 12 / 26 / 9, stop 3 %
    buy = crossover(macd, signal) and rsi <= 40 -> entry long, entry_price = close; sell mirrored with rsi >= 59
    position long and close < entry_price x 0.97 -> close (short mirrored); entry_price = na while flat

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is checked on closes and acts through strategy.close: an exit signal at the next open (rule 3; as
      #489638), not a broker stop. It uses the latest signal close, as written.
    * Entries reverse (REVERSAL INTENDED). State machine on the position held at each close; the close never undoes that
      bar's entry. No stop module. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the close-based stop is an exit signal.
    2 generic: PASS, MACD, RSI and a percentage stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted in original_sizing.txt.
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

NAME = "fmz_482891_macd_cross_rsi_close_stop_reversal"
FAMILY = "macd"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_pct": [3.0, 1.5],
    "rsi_ob": [59, 70],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_ob": 59, "rsi_os": 40, "stop_pct": 3.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    buy = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (rsi <= p["rsi_os"])).to_numpy()
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (rsi >= p["rsi_ob"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = p["stop_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, entry = 0, np.nan
    for i in range(m):
        if held == 0:
            entry = np.nan
        pos = held
        if buy[i]:
            pos, entry = 1, cv[i]
        if sell[i]:
            pos, entry = -1, cv[i]
        if held == 1 and pos == 1 and cv[i] < entry * (1 - k):
            pos = 0
        if held == -1 and pos == -1 and cv[i] > entry * (1 + k):
            pos = 0
        tgt[i] = pos
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
