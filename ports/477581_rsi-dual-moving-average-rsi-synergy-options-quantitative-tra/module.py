"""SMA 7 / 13 crossings against the RSI 17 side, hourly bars: the cross up with RSI under 43 goes long with a 0.5 % stop and 4 % target from the entry price; the cross down with RSI over 64 goes short, whose exit (sent with the long's levels) is on the wrong side and closes it at the open after its fill bar; reversing.
Port of FMZ strategy #477581 "双均线-RSI联动期权量化交易策略-Dual-Moving-Average-RSI-Synergy-Options-Quantitative-Trading-Strategy" (MA Crossover with RSI Debugging).

FMZ source id: 477581

Source
    https://www.fmz.com/strategy/477581 (PineScript v5, FMZ last modified 2025-01-06 15:24:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 91-154), SMA 7 / 13; RSI 17, 64 / 43; target 4 %, stop 0.5 % of strategy.position_avg_price (long formulas used for both sides)
    crossover(sma7, sma13) and rsi < 43 -> entry Buy;  crossunder and rsi > 64 -> entry Sell
    long: exit(Buy, limit = avg x 1.04, stop = avg x 0.995);  short: exit(Sell, limit = avg x 1.04, stop = avg x 0.995)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long's bracket is sent from the position's average price while it is held: scalar fractions
      of the entry fill, active from the fill (as #440797). The short's exit reuses the long levels: a
      buy limit 4 % above and a buy stop 0.5 % below the entry price are both marketable, so the exit sent
      at the close of the short's fill bar fills at the next open, as written: the short is closed one bar
      after its fill (a bar-close exit on the fill bar), with no stop inside that bar. The stops are a
      Series set on long fills only. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill; the short's wrong-side exit as written.
    2 generic: PASS, SMA crossings against the RSI side with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
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

NAME = "fmz_477581_sma7_13_cross_rsi17_avg_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [7, 5],
    "slow": [13, 30],
}
DEFAULT_PARAMS = {"fast": 7, "slow": 13, "rsi_length": 17, "tp_pct": 0.04, "sl_pct": 0.005}


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
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 43)
    se = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 64)
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    sf = se.shift(1, fill_value=False)
    return le, pd.Series(False, index=le.index), se, sf & ~le & ~se    # the short's marketable exit


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    lf = le.shift(1, fill_value=False)
    return {"sl_stop": pd.Series(float(p["sl_pct"]), index=le.index).where(lf),
            "tp_stop": pd.Series(float(p["tp_pct"]), index=le.index).where(lf)}


def portfolio_kwargs(**params):
    return {}
