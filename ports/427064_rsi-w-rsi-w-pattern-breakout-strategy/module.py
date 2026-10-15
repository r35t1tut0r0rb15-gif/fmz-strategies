"""RSI W pattern, long only: in an uptrend (EMA 20 above EMA 50), a W shape in RSI(5) whose last
value is between 30 and 65 goes long; the position is closed when RSI crosses above 75 while the
close is above the entry price, or when the close falls 8 % below the entry price.
Port of FMZ strategy #427064 "RSI-W Pattern Breakout Strategy".

FMZ source id: 427064

Source
    https://www.fmz.com/strategy/427064 (PineScript v4, FMZ last modified 2023-09-17 18:24:17).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 150-251), RSI 5, entry ceiling 65, EMA 50 / 20, stop 8 %
    W = rsi > rsi[1] and rsi >= 30 and rsi[1] < rsi[2] and rsi[2] > rsi[3] and rsi[3] < rsi[4]
        and (low[1] <= low[4] or low[3] <= low[4])
    ema(close, 20) > ema(close, 50) and W and 30 <= rsi <= 65 -> entry long
    crossover(rsi, 75) and close > position_avg_price -> close
    close < position_avg_price x (1 - 8 %) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * pyramiding = 2: the second entry (a repeated signal, or RSI crossing above 10 while long)
      is an add, i.e. sizing (criterion 4, stored in original_sizing.txt). The port enters only
      from flat, so position_avg_price is the entry fill price (the next bar's open).
    * The 8 % "stop" is a close-based exit (rule 3): an exit signal, never sl_stop.
    * At most one signal per bar; an exit is never on the entry's own signal bar.
    * FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close rules, exits on completed bars.
    2 generic: PASS, RSI levels and EMA lengths are dimensionless; the stop is a fraction of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the pyramid add is stored in original_sizing.txt, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427064_rsi_w_pattern_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [5, 7],
    "buy_rsi_entry": [65, 55],
    "stop_pct": [8.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_length": 5, "buy_rsi_entry": 65, "ema_long": 50, "ema_short": 20,
                  "stop_pct": 8.0, "tp_rsi": 75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _rsi(close, n):
    """Pine rsi: down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down), Wilder averages."""
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return pd.Series(val, index=close.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, low = bars_df["close"], bars_df["low"]
    r = _rsi(c, int(p["rsi_length"]))
    w = ((r > r.shift(1)) & (r >= 30) & (r.shift(1) < r.shift(2)) & (r.shift(2) > r.shift(3))
         & (r.shift(3) < r.shift(4)) & ((low.shift(1) <= low.shift(4)) | (low.shift(3) <= low.shift(4))))
    trend = (c.ewm(span=int(p["ema_short"]), adjust=False).mean()
             > c.ewm(span=int(p["ema_long"]), adjust=False).mean())
    entry = (trend & w & (r <= p["buy_rsi_entry"]) & (r >= 30)).to_numpy()
    tp_cross = ((r > p["tp_rsi"]) & (r.shift(1) <= p["tp_rsi"])).to_numpy()
    o, cv = bars_df["open"].to_numpy(dtype=float), c.to_numpy(dtype=float)
    stop = p["stop_pct"] / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, avg = 0, False, np.nan
    for i in range(m):
        if pending:                       # the entry fills at this bar's open
            pos, pending, avg = 1, False, o[i]
        if pos == 1:
            if (tp_cross[i] and cv[i] > avg) or cv[i] < avg * (1 - stop):
                lx[i], pos = True, 0
        elif not pending and entry[i]:
            le[i], pending = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
