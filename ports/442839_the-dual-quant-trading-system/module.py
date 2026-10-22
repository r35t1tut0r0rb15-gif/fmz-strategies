"""EMA 9 / 20 trend with a CCI 20 and RSI 9 / 20 crossing, 1-hour bars, 09:30-15:45 UTC: the fast EMA above the slow with the CCI over 100 and RSI 9 crossing over RSI 20 goes long, the mirror short; a
close under the ratcheted close-based stop, or leaving the session, closes; reversing.
Port of FMZ strategy #442839 "The Dual Quant Trading System" (EMA with RSI Cross Strategy).

FMZ source id: 442839

Source
    https://www.fmz.com/strategy/442839 (PineScript v5, FMZ last modified 2024-02-26 14:30:54).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-207), EMA 9 / 20; RSI 9 / 20; CCI 20 on hlc3; trail 0.5 $ (price units); session 0930-1545; qty 1
    longStop = Bull ? max(close - 0.5, longStop[1]) : 0;  shortStop = Bear ? min(close + 0.5, shortStop[1]) : 999999;  validSession = time("1", "0930-1545") not na
    Bull and cci > 100 and crossover(rsi9, rsi20) and validSession -> entry Long;  close < longStop or not validSession -> close Long;  shorts mirrored (cci < 100)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 0.5 trail is in price units: as a fraction of the close at the BTC reading of
      42000, 1.19e-5 x close. The session is read on the UTC bar open: bars opening 10:00-15:00 (the
      09:00 bar opens before 09:30). The close tests run at the bar close; each close acts only on a
      held position. The short's CCI test is under 100, as written. The quantity 1 is sizing.
      strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit trail -> fraction of the close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries and holds on bars opening 10:00-15:00 UTC (bar open time).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442839_ema_trend_cci_rsi_cross_session"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [9, 5],
    "cci_len": [20, 14],
}
DEFAULT_PARAMS = {"fast_len": 9, "cci_len": 20, "slow_len": 20, "rsi1": 9, "rsi2": 20, "trail_frac": 1.19e-05,
                  "s_start": 570, "s_end": 945}


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


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * md)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fe = c.ewm(span=int(p["fast_len"]), adjust=False).mean()
    se_ = c.ewm(span=int(p["slow_len"]), adjust=False).mean()
    bull, bear = (fe > se_).to_numpy(), (fe < se_).to_numpy()
    r1, r2 = _rsi(c, int(p["rsi1"])), _rsi(c, int(p["rsi2"]))
    up = ((r1 > r2) & (r1.shift(1) <= r2.shift(1))).to_numpy()
    dn = ((r1 < r2) & (r1.shift(1) >= r2.shift(1))).to_numpy()
    cci = _cci((h + lo + c) / 3, int(p["cci_len"])).to_numpy()
    t = bars_df.index.tz_convert("UTC")
    mins = t.hour * 60 + t.minute
    sess = (mins >= int(p["s_start"])) & (mins < int(p["s_end"]))
    cv = c.to_numpy(dtype=float)
    f = float(p["trail_frac"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, ls, ss = 0, 0.0, 999999.0
    for i in range(m):
        ls = max(cv[i] * (1 - f), ls) if bull[i] else 0.0
        ss = min(cv[i] * (1 + f), ss) if bear[i] else 999999.0
        new = held
        with np.errstate(invalid="ignore"):
            if bull[i] and cci[i] > 100 and up[i] and sess[i] and new != 1:
                new = 1
            if (cv[i] < ls or not sess[i]) and held == 1 and new == 1:
                new = 0
            if bear[i] and cci[i] < 100 and dn[i] and sess[i] and new != -1:
                new = -1
            if (cv[i] > ss or not sess[i]) and held == -1 and new == -1:
                new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
