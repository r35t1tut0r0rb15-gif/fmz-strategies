"""The template's demo rule, 1-minute bars: RSI 10 crossing over 80 sends both the long and the short entry (the short condition is the long one, as written), so from flat it goes short, from long it reverses short and from short it reverses long; a close 15 % against the entry, RSI 100 crossing under 40 or over 60 closes; a 100 % target from the entry.
Port of FMZ strategy #426563 "Universal Strategy Backtest Template" (Strategy Backtesting Template [MYN]).

FMZ source id: 426563

Source
    https://www.fmz.com/strategy/426563 (PineScript v5, FMZ last modified 2023-09-13 12:28:06).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-244), RSI 10 entry 80 / 20, RSI 100 exit 40 / 60; ADX filter off; TP 1-4 at 100 % (100 % of the position each); SL 15 % (close test); leverage 1
    longCondition = crossover(rsi(10), 80);  shortCondition = longConditionEntry (as written)
    long and not in a long -> entry Long;  short and not in a short -> entry Short;  exit(TP1..TP4, profit = 100 % of the avg price);  close < avg x 0.85 -> close Long (short mirror);  crossunder(rsi(100), 40) or crossover(rsi(100), 60) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * shortCondition repeats the LONG entry condition, as written (the short entry condition
      crossunder(rsi, 20) is computed but unused): on a signal bar the long entry is sent unless long and
      the short entry unless short, so the later call decides (flat -> short, long -> short, short ->
      long; weird case). The four targets are 100 % of the average price with 100 % of the position each:
      the first closes it all, a scalar 1.0 of the fill. The 15 % stop is a close test against the fill.
      The closes act only on a position the bar's entries leave unchanged. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The equity x leverage contracts are sizing. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop and RSI exits; target from the fill.
    2 generic: PASS, RSI threshold demo rule (as written).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: contracts = equity / close x leverage, 100 % of equity, capital 20000, commission 0.075 stored, not ported.
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

NAME = "fmz_426563_template_rsi10_over80_both_entries_rsi100_close_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "entry_level": [80.0, 70.0],
    "sl": [0.15, 0.05],
}
DEFAULT_PARAMS = {"entry_level": 80.0, "sl": 0.15, "tp": 1.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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
    o, c = bars_df["open"], bars_df["close"]
    r10, r100 = _rsi(c, 10), _rsi(c, 100)
    lv = float(p["entry_level"])
    sig = ((r10 > lv) & (r10.shift(1) <= lv)).to_numpy()
    xall = (((r100 < 40) & (r100.shift(1) >= 40)) | ((r100 > 60) & (r100.shift(1) <= 60))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sl = float(p["sl"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, avg = 0, np.nan
    for i in range(m):
        old = pos
        if sig[i] and old != 1:
            pos = 1                                        # entry Long (not in a long)
        if sig[i] and old != -1:
            pos = -1                                       # entry Short (not in a short), the later call
        if pos == old != 0:
            if old == 1 and cv[i] < avg * (1 - sl):
                pos = 0
            elif old == -1 and cv[i] > avg * (1 + sl):
                pos = 0
            elif xall[i]:
                pos = 0
        if pos != old and pos != 0 and i + 1 < m:
            avg = ov[i + 1]
        if pos == 1 and old != 1:
            le[i] = True
        elif pos == -1 and old != -1:
            se[i] = True
        elif pos == 0 and old == 1:
            lx[i] = True
        elif pos == 0 and old == -1:
            sx[i] = True
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
