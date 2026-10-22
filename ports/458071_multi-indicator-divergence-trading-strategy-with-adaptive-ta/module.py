"""RSI, MACD and stochastic crossings of their signal lines, 1-hour bars: all three crossing up on one bar goes long, the RSI and MACD crossing up without the stochastic goes short; each trade has a 20 % target and 10 % stop from the fill; reversing.
Port of FMZ strategy #458071 "Multi Indicator Divergence Trading Strategy with Adaptive Take Profit and Stop Loss" (Multi-Divergence Buy/Sell Strategy with TP and SL).

FMZ source id: 458071

Source
    https://www.fmz.com/strategy/458071 (PineScript v5, FMZ last modified 2024-07-29 17:02:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 209-275), RSI 14 vs its SMA 14; MACD 12 / 26 / 9; stochastic 14 vs its SMA 14; target 20 %, stop 10 % of the average price
    crossover(rsi, sma(rsi, 14)) and crossover(macd, signal) and crossover(stoch, sma(stoch, 14)) -> entry Buy;  the first two and not the third -> entry Sell
    exit(Buy, limit = avg x 1.2, stop = avg x 0.9);  exit(Sell, limit = avg x 0.8, stop = avg x 1.1)  (every bar while held)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "divergences" are plain crossings of each oscillator over its own average. The bracket comes
      from the average (fill) price and is sent every bar while a trade is open: ported active from the
      fill bar (#440797) as the fixed fractions 0.20 / 0.10 of the fill. The header's pyramiding remark
      is a comment only (no pyramiding is set). REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, oscillator signal-line crossings with a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_458071_rsi_macd_stoch_signal_cross_pct_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.20, 0.05],
    "sl_pct": [0.10, 0.03],
}
DEFAULT_PARAMS = {"tp_pct": 0.20, "sl_pct": 0.10, "rsi_len": 14, "fast": 12, "slow": 26, "signal": 9,
                  "stoch_len": 14}


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


def _xover(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    stoch = 100 * (c - ll) / (hh - ll)
    rd = _xover(r, r.rolling(14).mean())
    md = _xover(macd, sig)
    sd = _xover(stoch, stoch.rolling(14).mean())
    le = rd & md & sd
    se = rd & md & ~sd
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
