"""MACD 12 / 26 / 9 crossings against the zero line in the London and New York hours, 1-hour bars: the signal line crossing over the MACD above zero goes short, crossing under it below zero goes long, between 08:00 and 20:00 UTC, each with a 10-tick stop and 15-tick target; reversing.
Port of FMZ strategy #458076 "Multi Timeframe Market Momentum Crossover Strategy" (交易霸傑15掏金策略 (MACD session crossings)).

FMZ source id: 458076

Source
    https://www.fmz.com/strategy/458076 (PineScript v5, FMZ last modified 2024-07-29 17:10:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 170-221), MACD 12 / 26 / 9; London 08:00-17:00, New York 13:30-20:00 (GMT+0, bar time inclusive); stop 10, target 15 ticks of the signal close; qty 1 contract
    crossover(signal, macd) and macd > 0 and in session -> entry Short + exit(limit = close - 15 ticks, stop = close + 10 ticks)
    crossunder(signal, macd) and macd < 0 and in session -> entry Long + exit(limit = close + 15 ticks, stop = close - 10 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The two windows join into 08:00-20:00 UTC on the bar's open time, both ends included (#435514).
      The 10 / 15 ticks are 1.0 / 1.5 at the 0.1 tick, ported as ATR multiples at the 1-hour reading
      (~150): 0.0067 / 0.01 ATR 14 from the bar before the fill. The equity-risk amount is computed but
      never used; the fixed 1-contract quantity is not ported (sizing is the optimisation layer's).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the tick bracket as ATR multiples.
    2 generic: PASS, MACD signal crossings beyond zero in set hours.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed 1-contract quantity and the unused risk amount stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 08:00-20:00 UTC on the bar open, both ends included (London 08:00-17:00 joined with New York 13:30-20:00, GMT+0 as written).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458076_macd_signal_cross_beyond_zero_session_tick_bracket_reversal"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.0067, 1.0],
    "tp_atr": [0.01, 1.5],
}
DEFAULT_PARAMS = {"sl_atr": 0.0067, "tp_atr": 0.01, "atr_len": 14, "fast": 12, "slow": 26, "signal": 9}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    ix = bars_df.index
    mins = pd.Series(ix.hour * 60 + ix.minute, index=ix)
    sess = (mins >= 8 * 60) & (mins <= 20 * 60)
    se = (sig > macd) & (sig.shift(1) <= macd.shift(1)) & (macd > 0) & sess
    le = (sig < macd) & (sig.shift(1) >= macd.shift(1)) & (macd < 0) & sess
    false = pd.Series(False, index=ix)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": (float(p["sl_atr"]) * a).shift(1), "tp_stop": (float(p["tp_atr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
