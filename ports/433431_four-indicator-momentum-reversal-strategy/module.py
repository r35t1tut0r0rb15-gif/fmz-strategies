"""EMA 4 / 8 crosses confirmed by a smoothed RSI and CCI, 45-minute bars: the EMA 4 crossing above the EMA 8 with the RSI of
the EMA 14 at 65 or more and the CCI 14 at or above zero goes long; the mirror (RSI 35 or less, CCI at or below zero)
goes short. Each trade carries a 120-tick target and a 96-tick stop, which become ATR multiples.
Port of FMZ strategy #433431 "Four Indicator Momentum Reversal Strategy" (Moving Average Exponential (four indicators)).

FMZ source id: 433431

Source
    https://www.fmz.com/strategy/433431 (PineScript v4, FMZ last modified 2023-11-27 15:51:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 148-263), EMA 4 / 8; RSI 14 on ema(close, 14); CCI 14; TP 120 / SL 96 ticks
    rsi = 100 - 100 / (1 + rma(up(change(ema(close, 14))), 14) / rma(down(...), 14))
    crossover(ema4, ema8) and rsi >= 65 and cci14 >= 0 -> entry long;  crossunder and rsi <= 35 and cci14 <= 0 -> entry short
    exit(profit = 120, loss = 96) on both

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the bracket is in ticks (12 / 9.6 USD on the header's BTC_USDT, mintick 0.1, about
      0.1 / 0.08 ATR of 45-minute BTC, ATR about 120 USD). It becomes tp_atr / sl_atr x Wilder ATR 14
      of the signal bar as fractions of its close, shifted one bar inside stops() and re-based on the
      fill. The level lines (a x mintick, b x mintick) are plots only.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick bracket quoted in original_sizing.txt.
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

NAME = "fmz_433431_ema_4_8_rsi_cci_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [0.1, 1.0],
    "sl_atr": [0.08, 0.8],
}
DEFAULT_PARAMS = {"fast": 4, "slow": 8, "rsi_len": 14, "cci_len": 14, "atr_len": 14, "tp_atr": 0.1, "sl_atr": 0.08}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        mu = win.mean(axis=1)
        md = np.abs(win - mu[:, None]).mean(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[n - 1:] = (v[n - 1:] - mu) / (0.015 * md)
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["rsi_len"])
    ch = c.ewm(span=n, adjust=False).mean().diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    cci = _cci(c, int(p["cci_len"]))
    le = ((f > s) & (f.shift(1) <= s.shift(1)) & (rsi >= 65) & (cci >= 0)).astype(bool)
    se = ((f < s) & (f.shift(1) >= s.shift(1)) & (rsi <= 35) & (cci <= 0)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1), "tp_stop": (af * float(p["tp_atr"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
