"""Rainbow MA, 2-hour bars: SMA 12 of hlc3 and six further SMA 3 smoothings of it; when the first line
becomes the highest of the seven (with RSI 12 between 35 and 65 and the previous RSI 9 outside 44-56)
go long, when it becomes the lowest go short; close when it falls inside the fan or turns without the
RSI filter.
Port of FMZ strategy #428053 "Rainbow Moving Average Trading Strategy".

FMZ source id: 428053

Source
    https://www.fmz.com/strategy/428053 (PineScript v4, FMZ last modified 2023-09-28 11:01:59).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 192-317), SMA 12 of hlc3, displacement 3, RSI 12 (35 / 65), RSI 9 (44 / 56)
    ma1 = sma(hlc3, 12); ma2..ma7 = sma(previous, 3); colour = up if ma1 is the max, down if the min, else none
    normal = 35 < rsi12 < 65 and (rsi9[1] < 44 or rsi9[1] > 56)
    Buy = colour turns up and normal -> entry long; Sell = turns down and normal -> entry short
    exit = colour turns none; filter = colour changes without Buy / Sell / exit -> close both sides

Interpretation choices (Pine rules in SURVEY_README.md)
    * The RSI filter is enabled (default); SMA type (default).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and RSI levels.
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

NAME = "fmz_428053_rainbow_ma_rsi_filter"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma1_len": [12, 24],
    "dis_len": [3, 5],
}
DEFAULT_PARAMS = {"ma1_len": 12, "dis_len": 3, "rsi_len_1": 12, "rsi_ovb": 65, "rsi_ovs": 35,
                  "rsi_len_2": 9, "rsi_mid_top": 56, "rsi_mid_bot": 44}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma(-d.clip(upper=0), n)
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo + c) / 3
    mas = [src.rolling(int(p["ma1_len"])).mean()]
    for _ in range(6):
        mas.append(mas[-1].rolling(int(p["dis_len"])).mean())
    stack = pd.concat(mas, axis=1)
    m1 = mas[0]
    colour = np.where(m1 == stack.max(axis=1), 1, np.where(m1 == stack.min(axis=1), -1, 0))
    colour = np.where(stack.isna().any(axis=1), 0, colour)
    r1, r2 = _rsi(c, int(p["rsi_len_1"])), _rsi(c, int(p["rsi_len_2"]))
    normal = ((r1 > p["rsi_ovs"]) & (r1 < p["rsi_ovb"]) &
              ((r2.shift(1) < p["rsi_mid_bot"]) | (r2.shift(1) > p["rsi_mid_top"]))).to_numpy()
    m = len(colour)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(1, m):
        changed = colour[i] != colour[i - 1]
        buy = changed and colour[i] == 1 and normal[i]
        sell = changed and colour[i] == -1 and normal[i]
        ext = changed and colour[i] == 0
        filt = changed and not buy and not sell and not ext
        if buy:
            pos = 1
        elif sell:
            pos = -1
        elif ext or filt:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
