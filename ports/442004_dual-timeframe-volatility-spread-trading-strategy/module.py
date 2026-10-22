"""B-Xtrender zero crossings, 2-hour bars, long only: from flat, the short-term Xtrender (RSI 14 of EMA 7 - EMA 28, minus 50) crossing over zero goes long, or else the long-term one (RSI 14 of EMA 28,
minus 50); the long closes when the Xtrender that opened it crosses back under zero.
Port of FMZ strategy #442004 "Dual Timeframe Volatility Spread Trading Strategy" (MavXtrender).

FMZ source id: 442004

Source
    https://www.fmz.com/strategy/442004 (PineScript v4, FMZ last modified 2024-02-18 15:31:32).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 135-188), short term 7 / 4 / 2, long term 4 / 2, factors on (x 7: EMA 28, RSI 14, EMA 28, RSI 14); both terms traded; dates 2018-2020
    shortX = rsi(ema(close, 7) - ema(close, 28), 14) - 50;  longX = rsi(ema(close, 28), 14) - 50
    crossover(shortX, 0) -> entry ShortTerm (qty equity / (close x 2));  crossover(longX, 0) -> entry LongTerm;  crossunder(shortX, 0) or time > finish -> close ShortTerm;  crossunder(longX, 0) or time > finish -> close LongTerm

Interpretation choices (Pine rules in SURVEY_README.md)
    * With UseFactors the lengths are multiplied by 7 as written. strategy() leaves pyramiding at its
      default, so only one long entry can be open: while either is open the other is refused, and each close
      names its own entry. The time > finish test is the author's bounded date window (to 2020) and is
      dropped like other date windows. Long only. The quantity rule is sizing. FREQ = "2h" from the
      backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Xtrender zero crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity / close quantity rule stored.
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

NAME = "fmz_442004_b_xtrender_zero_cross_own_exit_long"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_sma": [7, 5],
    "rsi_factor": [2, 3],
}
DEFAULT_PARAMS = {"short_sma": 7, "rsi_factor": 2, "lma_factor": 4, "long_ma_factor": 4, "long_rsi_factor": 2}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s = int(p["short_sma"])
    lma = int(round(s * int(p["lma_factor"])))
    srsi = int(round(s * int(p["rsi_factor"])))
    lgma = int(round(s * int(p["long_ma_factor"])))
    lgrsi = int(round(s * int(p["long_rsi_factor"])))
    sx_ = _rsi(c.ewm(span=s, adjust=False).mean() - c.ewm(span=lma, adjust=False).mean(), srsi) - 50
    lx_ = _rsi(c.ewm(span=lgma, adjust=False).mean(), lgrsi) - 50
    su = ((sx_ > 0) & (sx_.shift(1) <= 0)).to_numpy()
    sd = ((sx_ < 0) & (sx_.shift(1) >= 0)).to_numpy()
    lu = ((lx_ > 0) & (lx_.shift(1) <= 0)).to_numpy()
    ld = ((lx_ < 0) & (lx_.shift(1) >= 0)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = 0   # 0 flat, 1 the ShortTerm entry, 2 the LongTerm entry
    for i in range(m):
        if held == 0:
            if su[i] and i + 1 < m:
                le[i], held = True, 1
            elif lu[i] and i + 1 < m:
                le[i], held = True, 2
        elif (held == 1 and sd[i]) or (held == 2 and ld[i]):
            lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
