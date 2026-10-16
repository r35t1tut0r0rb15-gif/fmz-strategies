"""CoG + SSL + ROC: long when the close breaks above a linear-regression centre-of-gravity band, or
when the SSL channel points up while the market is moving (smoothed 2-bar ROC beyond +-5 %); short
on the mirror. Each new side gets a stop 2 x ATR(1) beyond the signal bar's close.
Port of FMZ strategy #427304 "Center of Gravity SSL Channel Trend Following Strategy".

FMZ source id: 427304

Source
    https://www.fmz.com/strategy/427304 (PineScript v4, FMZ last modified 2023-09-19 21:30:23).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 179-280), SSL 12 / 13, CoG linreg 25 offset 5 +-6 %, ROC 2 / 10 %,
ATR stop 1 x 2
    Hlv = close > sma(high, 12) ? 1 : close < sma(low, 13) ? -1 : Hlv[1]; sslUp > sslDown <=> Hlv > 0
    pos = close > linreg(close, 25, 5) + 6 % close ? 1 : close < ... - 6 % close ? -1 : pos[1]
    moving = |ema(100 (close - close[2]) / close[2], 1)| > 5
    long = pos == 1 or (Hlv > 0 and moving); short = pos == -1 or (Hlv < 0 and moving)
    long -> entry L; short -> entry S; exit(stop = close[signal bar] -+ 2 atr(1)) from the bar after the signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the CoG band +-6 % of the close becomes +- `cog_atr` x Wilder ATR(14). The ROC
      threshold is a percent change of price (dimensionless), kept.
    * The stop is fixed at the first signal of a side (close -+ 2 x ATR(1)); ported via stops() as
      the fraction 2 x ATR(1) / close of the signal bar, shifted one bar (known at the fill bar's
      open) and re-based on each fill. Pine keeps the first signal's LEVEL for a re-entry after a
      stop-out without an opposite signal; the port re-bases it on the re-entry (stated deviation).
    * Entries are emitted on every bar the condition holds (Pine re-enters after a stop-out); a bar
      with both conditions goes to the side opposite the last signalled side (Pine reverses the side
      held). Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * testPeriod() is the constant true.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is fixed at the signal.
    2 generic: ADAPT, the 6 % CoG band -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity and commission stored; the stop ported via stops().
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427304 (3 members, best partner #429390, Jaccard 0.697); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427304_cog_ssl_roc"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cog_atr": [4.0, 2.0],
    "pcnt_change": [10.0, 4.0],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"len1": 12, "len2": 13, "length": 25, "offset": 5, "cog_atr": 4.0, "atr_length": 14,
                  "roc_length": 2, "pcnt_change": 10.0, "atr_stop_period": 1, "atr_mult": 2.0}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def _linreg(x, n, offset):
    """Pine linreg(x, n, offset): the least-squares line over the last n bars, evaluated n - 1 - offset bars
    after the window's first bar (offset 0 = the current bar)."""
    t = np.arange(n, dtype=float)
    tm = t.mean()
    den = ((t - tm) ** 2).sum()

    def f(w):
        b = ((t - tm) * (w - w.mean())).sum() / den
        a = w.mean() - b * tm
        return a + b * (n - 1 - offset)
    return x.rolling(n).apply(f, raw=True)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    sh, sl = h.rolling(int(p["len1"])).mean(), lo.rolling(int(p["len2"])).mean()
    cv, shv, slv = c.to_numpy(dtype=float), sh.to_numpy(), sl.to_numpy()
    lg = _linreg(c, int(p["length"]), int(p["offset"])).to_numpy()
    band = (p["cog_atr"] * _atr(bars_df, int(p["atr_length"]))).to_numpy()
    k = int(p["roc_length"])
    roc = 100 * (c - c.shift(k)) / c.shift(k)
    emaroc = roc.ewm(span=max(int(k / 2), 1), adjust=False).mean().to_numpy()
    moving = (emaroc > p["pcnt_change"] / 2) | (emaroc < -p["pcnt_change"] / 2)
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    hlv = pos = 0
    last_side = 0
    for i in range(m):
        if cv[i] > shv[i]:
            hlv = 1
        elif cv[i] < slv[i]:
            hlv = -1
        if cv[i] > lg[i] + band[i]:
            pos = 1
        elif cv[i] < lg[i] - band[i]:
            pos = -1
        lc = pos == 1 or (hlv > 0 and moving[i])
        sc = pos == -1 or (hlv < 0 and moving[i])
        if lc and sc:
            lc, sc = last_side != 1, last_side == 1
        if lc:
            le[i] = True
        if sc:
            se[i] = True
        if lc and last_side != 1:
            last_side = 1
        elif sc and last_side != -1:
            last_side = -1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = p["atr_mult"] * _atr(bars_df, int(p["atr_stop_period"])) / bars_df["close"]
    return {"sl_stop": frac.shift(1)}


def portfolio_kwargs(**params):
    return {}
