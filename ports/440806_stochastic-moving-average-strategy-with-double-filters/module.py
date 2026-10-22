"""Oversold stochastic turns, 1-minute bars, long only: K above D with K at or under 25 and the close at or above the close two bars back goes long; the close crossing under the EMA 38 with K at or
above 65, or a close 13 % under the entry, closes.
Port of FMZ strategy #440806 "Stochastic Moving Average Strategy with Double Filters" (Stochastic & MA).

FMZ source id: 440806

Source
    https://www.fmz.com/strategy/440806 (PineScript v5, FMZ last modified 2024-02-02 11:28:58).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-188), stochastic 21 / 6 / 4; oversold 25; n 2; EMA 38; k filter 65; stop 13 % x leverage 1
    entry1 = k > d and k <= 25 and close >= close[2] -> entry Long;  exit1 = crossunder(close, ema38) and k >= 65 -> close;  exit2 = close < avg price x (1 - 13 % x leverage) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a close test against the fill price, sent at the next open (not an order). The
      leverage input only scales the stop distance (1 by default). Long only. No sizing code. FREQ =
      "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-tested stop.
    2 generic: PASS, stochastic, EMA and a close stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
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

NAME = "fmz_440806_stoch_oversold_turn_ema_exit_long"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [21, 14],
    "lossp": [13, 5],
}
DEFAULT_PARAMS = {"length": 21, "lossp": 13, "leverage": 1, "n": 2, "filtro": 65, "oversold": 25, "smooth_k": 6,
                  "smooth_d": 4, "ema_period": 38}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["length"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["smooth_k"])).mean()
    d = k.rolling(int(p["smooth_d"])).mean()
    e = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    buy = ((k > d) & (k <= float(p["oversold"])) & (c >= c.shift(int(p["n"])))).to_numpy()
    x1 = ((c < e) & (c.shift(1) >= e.shift(1)) & (k >= float(p["filtro"]))).to_numpy()
    lf = float(p["lossp"]) / 100 * float(p["leverage"])
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, x = 0, np.nan
    for i in range(m):
        new = 1 if buy[i] else pos
        if pos == 1 and new == 1 and (x1[i] or cv[i] < x * (1 - lf)):
            new = 0
        if new == 1 and pos != 1 and i + 1 < m:
            x = ov[i + 1]                                # the fill of the new long
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
