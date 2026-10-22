"""MACD 12 / 26 / 9 crossings with RSI 14 at or under 40 / at or over 59, 1-minute bars: the up-cross with a low RSI goes long, the down-cross with a high RSI goes short; a close 3 % against the last signal close closes; reversing.
Port of FMZ strategy #482891 "使用RSI和MACD双重过滤的动态止损趋势跟踪策略-Dynamic-Stop-Loss-Trend-Following-Strategy-with-RSI-and-MACD-Dual-Filtering" (EAG MACD + RSI Strategy).

FMZ source id: 482891

Source
    https://www.fmz.com/strategy/482891 (PineScript v5, FMZ last modified 2025-02-20 16:50:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-151), RSI 14 / 59 / 40; MACD 12 / 26 / 9; stop 3 % on closes; 10 % of equity, capital 300, commission 0.1 %; MPL 2.0 notice (eagle916)
    crossover(macd, signal) and rsi <= 40 -> entry Compra, entry_price := close;  crossunder(macd, signal) and rsi >= 59 -> entry Venta, entry_price := close
    flat -> entry_price := na;  long and close < entry_price x 0.97 -> close Compra;  short and close > entry_price x 1.03 -> close Venta

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is checked on bar closes and sent as a close (an exit signal, no stop module). entry_price
      is the last signal's close: a repeat signal on the side held resets it (the entry itself adds
      nothing), as written; it is cleared on a flat bar. Followed in a loop. An entry on the other side
      reverses (REVERSAL INTENDED). The 10 % of equity size and the capital are sizing; the commission is
      a cost (the house cost model applies). The MPL 2.0 notice is kept with the verbatim copy (ported,
      stated). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based percent stop.
    2 generic: PASS, MACD crossings with RSI levels.
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

NAME = "fmz_482891_macd_cross_rsi14_40_59_close_stop3pct_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_loss_percent": [3.0, 1.5],
    "rsi_length": [14, 7],
}
DEFAULT_PARAMS = {"stop_loss_percent": 3.0, "rsi_length": 14, "rsi_ob": 59, "rsi_os": 40, "fast": 12, "slow": 26,
                  "signal": 9}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]

    def ema(x, n):
        return x.ewm(span=int(n), adjust=False).mean()

    macd = ema(c, p["fast"]) - ema(c, p["slow"])
    sig = ema(macd, p["signal"])
    r = _rsi(c, int(p["rsi_length"]))
    buy = ((macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r <= float(p["rsi_os"]))).to_numpy()
    sell = ((macd < sig) & (macd.shift(1) >= sig.shift(1)) & (r >= float(p["rsi_ob"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    q = float(p["stop_loss_percent"]) / 100
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend = 0, None
    ep = np.nan
    for i in range(m):
        if pend is not None:
            pos, pend = pend, None
        if pos == 0:
            ep = np.nan
        if buy[i]:
            le[i], ep, pend = True, cv[i], 1
        if sell[i]:
            se[i], ep, pend = True, cv[i], -1
        if pos > 0 and cv[i] < ep * (1 - q) and not (le[i] or se[i]):
            lx[i], pend = True, 0
        if pos < 0 and cv[i] > ep * (1 + q) and not (le[i] or se[i]):
            sx[i], pend = True, 0
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le & ~se), S(lx), S(se), S(sx)


def portfolio_kwargs(**params):
    return {}
