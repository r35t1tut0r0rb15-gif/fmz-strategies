"""BB + RSI + Aroonish (A22): within the last two bars the close crossed back above the lower
Bollinger band (20, 2.5) and RSI(4) crossed back above 20, with the "Aroonish" low-side confirmation:
go long; the mirror at the upper band and RSI 80 goes short; each position is closed 3 bars after its
signal.
Port of FMZ strategy #427468 "Configurable BBRSIAroon Strategy Backtest".

FMZ source id: 427468

Source
    https://www.fmz.com/strategy/427468 (PineScript v4, FMZ last modified 2023-09-21 15:05:38).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 158-240), Aroonish 4 / 50, RSI 4 (20 / 80), BB 20 x 2.5, 3 bars
    up = 100 (-highestbars(high, 5) + 4) / 4; lo = 100 (-lowestbars(low, 5) + 4) / 4
    confLong = lo >= 50 and up < lo; confShort = up >= 50 and up > lo
    long = (crossover(close, BBlow) or its [1]) and confLong and (crossover(rsi, 20) or its [1])
    short = (crossunder(close, BBup) or its [1]) and confShort and (crossunder(rsi, 80) or its [1])
    long -> entry long; long[3] -> close long (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written the "Aroonish" lines use -highestbars (a value from 100 to 200), so they are not
      the classic Aroon; ported literally. highestbars / lowestbars include the current bar; ties
      go to the most recent bar.
    * The 3-bar exit is an explicit exit signal (not max_hold_time). inDateRange is the constant true.
    * strategy.entry reverses: REVERSAL INTENDED.
    * stdev is the population standard deviation. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and bar-count exits.
    2 generic: PASS, oscillator levels, bands in standard deviations, bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427468_bb_rsi_aroonish"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.5, 2.0],
    "rsi_length": [4, 8],
    "n_bars": [3, 6],
}
DEFAULT_PARAMS = {"aroon_length": 4, "aroon_conf": 50, "rsi_length": 4, "rsi_os": 20, "rsi_ob": 80,
                  "bb_length": 20, "bb_mult": 2.5, "n_bars": 3}


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
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return pd.Series(val, index=close.index)


def _bars_offset(v, w, highest):
    m = len(v)
    out = np.full(m, np.nan)
    for t in range(w - 1, m):
        best, off = v[t], 0
        for k in range(1, w):
            x = v[t - k]
            if (x > best) if highest else (x < best):
                best, off = x, -k
        out[t] = off
    return out


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
    L = int(p["aroon_length"])
    hb = _bars_offset(h.to_numpy(dtype=float), L + 1, True)
    lb = _bars_offset(lo.to_numpy(dtype=float), L + 1, False)
    up = 100 * (-hb + L) / L
    dn = 100 * (-lb + L) / L
    conf_l = (dn >= p["aroon_conf"]) & (up < dn)
    conf_s = (up >= p["aroon_conf"]) & (up > dn)
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["bb_length"])
    basis, dev = c.rolling(n).mean(), p["bb_mult"] * c.rolling(n).std(ddof=0)
    bu, bl = basis + dev, basis - dev
    x_bl = (c > bl) & (c.shift(1) <= bl.shift(1))
    x_bu = (c < bu) & (c.shift(1) >= bu.shift(1))
    x_os = (r > p["rsi_os"]) & (r.shift(1) <= p["rsi_os"])
    x_ob = (r < p["rsi_ob"]) & (r.shift(1) >= p["rsi_ob"])
    sh = lambda s: s.shift(1, fill_value=False)
    long_c = ((x_bl | sh(x_bl)) & (x_os | sh(x_os))).to_numpy() & conf_l
    short_c = ((x_bu | sh(x_bu)) & (x_ob | sh(x_ob))).to_numpy() & conf_s
    k = int(p["n_bars"])
    lexit = np.concatenate((np.zeros(k, dtype=bool), long_c[:-k]))
    sexit = np.concatenate((np.zeros(k, dtype=bool), short_c[:-k]))
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and lexit[i]:
            pos = 0
        elif pos == -1 and sexit[i]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
