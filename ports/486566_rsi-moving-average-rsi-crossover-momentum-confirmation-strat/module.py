"""SMA 20 / 30 crossings with RSI 14 over 25 / under 75, hourly bars, long only: the up-cross goes long; a close 2 % over the signal close, or the down-cross, closes.
Port of FMZ strategy #486566 "滑动平均-RSI-交叉动量确认策略-Moving-Average-RSI-Crossover-Momentum-Confirmation-Strategy" (SMA+RSI Strategy).

FMZ source id: 486566

Source
    https://www.fmz.com/strategy/486566 (PineScript v6, FMZ last modified 2025-03-14 09:35:47).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-236), SMA 20 / 30; RSI 14 / 75 / 25; take profit 2 % on closes (on); half-position option off
    crossover(sma20, sma30) and rsi > 25 -> buy state, entry := close, entry Buy;  crossunder and rsi < 75 -> sell state
    buy state and close >= entry x 1.02 -> close Buy;  sell signal -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The take-profit is checked on bar closes and sent as a close (an exit signal, no stop module); the
      buy state stays set after it, so later closes at the level do nothing while flat, as written. The
      half-position option is off by default. Long only. No sizing code. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based percent target.
    2 generic: PASS, SMA crossings with an RSI filter and a percent target.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_486566_sma20_30_cross_rsi_filter_close_tp2pct_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_short_period": [20, 10],
    "take_profit_perc": [2.0, 4.0],
}
DEFAULT_PARAMS = {"sma_short_period": 20, "take_profit_perc": 2.0, "sma_long_period": 30, "rsi_period": 14,
                  "rsi_ob": 75, "rsi_os": 25}


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
    f = c.rolling(int(p["sma_short_period"])).mean()
    s = c.rolling(int(p["sma_long_period"])).mean()
    r = _rsi(c, int(p["rsi_period"]))
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (r > float(p["rsi_os"]))).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & (r < float(p["rsi_ob"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    q = float(p["take_profit_perc"]) / 100
    m = len(cv)
    lx = np.zeros(m, dtype=bool)
    in_buy = False
    ep = np.nan
    for i in range(m):
        if buy[i]:
            in_buy, ep = True, cv[i]
        if sell[i]:
            in_buy = False
        if (in_buy and cv[i] >= ep * (1 + q)) or sell[i]:
            lx[i] = True
    le = pd.Series(buy, index=c.index)
    false = pd.Series(False, index=c.index)
    return le, pd.Series(lx, index=c.index) & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
