"""Ehlers zero-lag EMA crossings with an error filter and a tick bracket, 4-hour bars: the error-corrected EMA (period 20) crossing over the EMA with the least error above 0.05 % of the price goes long, the
cross under short; a 70-tick stop and a 5-tick-activated, 15-tick trailing stop (as ATR multiples); reversing.
Port of FMZ strategy #442127 "Adaptive Zero Lag Exponential Moving Average Quantitative Trading Strategy" (AZLEMA).

FMZ source id: 442127

Source
    https://www.fmz.com/strategy/442127 (PineScript v3, FMZ last modified 2024-02-19 15:38:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-256), source close; period 20; adaptive Off; gain limit 10; threshold 0.05; SL 70, TP 5 (trail activation), trail offset 15 ticks; risk 0.01
    EMA = a src + (1 - a) nz(EMA[1]), a = 2 / 21;  for gain in -1 .. 1 step 0.1: EC = a (EMA + g (src - nz(EC[1]))) + (1 - a) nz(EC[1]), keep the least |src - EC|;  EC with the best gain
    buy = crossover(EC, EMA) and 100 LeastError / src > 0.05 -> entry BUY, exit(loss = 70, trail_points = 5, trail_offset = 15);  sell = crossunder -> entry SELL, same exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the adaptive method Off the period is 20; the EMA and EC start from 0 (nz) as written. The
      exits are tick counts: 70 ticks (7 price units at mintick 0.1 on the BTC reading) is a stop of
      0.0175 ATR at the 4-hour ATR(14) reading of about 400; the trail activates after 5 ticks (0.5 units,
      about 1.19e-05 of the price) and trails 15 ticks (1.5 units, about 0.00375 ATR) behind the best
      price: the house trail {"type": "volatility", "atr_n": 14, "k": 0.00375, "anchor": "high_low",
      "activate_after": 1.19e-05} (stated approximation, as #437390; mark trailing_stop). The stop is
      sl = 0.0175 ATR / close of the signal bar, shifted one bar inside stops(). strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark
      coarse_bar_stop. The risk-based lots are sizing. FREQ = "4h" from the backtest header (bars on UTC
      multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick stop and trail -> ATR multiples and a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot size and the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442127_zero_lag_ema_cross_error_filter_tick_trail"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [20, 40],
    "threshold": [0.05, 0.1],
}
DEFAULT_PARAMS = {"period": 20, "threshold": 0.05, "gain_limit": 10, "atr_len": 14, "sl_atr": 0.0175,
                  "trail_k": 0.00375, "trail_activate": 1.19e-05}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cv = c.to_numpy(dtype=float)
    a = 2.0 / (int(p["period"]) + 1)
    gl = int(p["gain_limit"])
    gains = np.arange(-gl, gl + 1) / 10.0
    m = len(cv)
    ema = np.zeros(m)
    ec = np.zeros(m)
    lerr = np.zeros(m)
    e_prev = ec_prev = 0.0
    for i in range(m):
        e = a * cv[i] + (1 - a) * e_prev
        trial = a * (e + gains * (cv[i] - ec_prev)) + (1 - a) * ec_prev
        err = np.abs(cv[i] - trial)
        k = int(np.argmin(err))
        lerr[i] = min(err[k], 1000000.0)
        x = a * (e + gains[k] * (cv[i] - ec_prev)) + (1 - a) * ec_prev
        ema[i], ec[i] = e, x
        e_prev, ec_prev = e, x
    es, xs = pd.Series(ema, index=c.index), pd.Series(ec, index=c.index)
    ok = pd.Series(100 * lerr / cv > float(p["threshold"]), index=c.index)
    buy = (xs > es) & (xs.shift(1) <= es.shift(1)) & ok
    sell = (xs < es) & (xs.shift(1) >= es.shift(1)) & ok
    false = pd.Series(False, index=c.index)
    return buy, false, sell & ~buy, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    sl = float(p["sl_atr"]) * _rma(tr, int(p["atr_len"])) / c
    return {"sl_stop": sl.shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
