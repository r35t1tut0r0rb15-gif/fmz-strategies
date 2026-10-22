"""Overbought band pierces, 2-hour bars, short only: an RSI 14 over 70 with the MACD under its signal and the close over the upper Bollinger band (20 / 2) sells short, with a 3 % stop and a 6 % target from the fill.
Port of FMZ strategy #454731 "超级三指标RSI-MACD-BB动量反转策略-Super-Triple-Indicator-RSI-MACD-BB-Momentum-Reversal-Strategy" (Short DOTUSDT con Alertas).

FMZ source id: 454731

Source
    https://www.fmz.com/strategy/454731 (PineScript v4, FMZ last modified 2024-06-21 14:10:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 194-241), RSI 14 over 70; MACD 12 / 26 / 9; Bollinger 20 / 2; stop 3 %, target 6 % of the average price
    rsi > 70 and macd < signal and close > upper -> entry Short;  exit(stop = avg x 1.03, limit = avg x 0.94) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a state (repeats ignored while short). The bracket is sent every bar from the
      average (fill) price, na while flat: ported active from the fill bar (#440797) as fixed fractions
      0.03 / 0.06 of the fill. Short only: Opposite entries cannot occur. Stop module: portfolio_kwargs
      {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "2h" from the
      backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, overbought band pierces with a bearish MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Short only: Opposite entries cannot occur.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_454731_overbought_band_pierce_macd_bearish_short"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ob": [70, 80],
    "sl_pct": [0.03, 0.05],
    "tp_pct": [0.06, 0.03],
}
DEFAULT_PARAMS = {"ob": 70.0, "sl_pct": 0.03, "tp_pct": 0.06, "rsi_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    upper = c.rolling(20).mean() + 2 * c.rolling(20).std(ddof=0)
    se = (r > float(p["ob"])) & (macd < sig) & (c > upper)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
