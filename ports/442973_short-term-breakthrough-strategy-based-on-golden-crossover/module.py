"""RSI 3 pullbacks against an SMA 200 trend, 1-hour bars: from flat, the close above the SMA 200 but under the EMA 21 with the RSI 3 under 20 goes long, the mirror (RSI over 80) short; the long has a 1 %
stop and 1 % target from the fill; bar-close reversals of the EMA 21 test close either side.
Port of FMZ strategy #442973 "Short term Breakthrough Strategy Based on Golden Crossover" (simple pull back).

FMZ source id: 442973

Source
    https://www.fmz.com/strategy/442973 (PineScript v5, FMZ last modified 2024-02-27 17:46:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-159), SMA 200, EMA 21; RSI 3 (20 / 80); stop 1 %, target 1 % (long only); 100 % of equity
    flat and close > sma200 and close < ema21 and rsi3 < 20 -> entry Long;  flat and close < sma200 and close > ema21 and rsi3 > 80 -> entry Short
    exit(Cut, Long, stop = avg (1 - 1 %), limit = avg (1 + 1 %));  close > ema21 and close < low[1] and long -> close Long;  close < ema21 and close > high[1] and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent every bar from the average (fill) price for the long only; on the flat signal
      bar it is na, so it is ported active from the fill bar (#440797) as fixed fractions 0.01 / 0.01 of
      the fill; the short has no bracket, as written. Entries come only from flat. The date filter is
      set to true. Stop module: portfolio_kwargs {} (driver D4). The 100 % of equity size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed from the fill.
    2 generic: PASS, RSI pullbacks against the trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442973_rsi3_pullback_sma200_long_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "malong": [200, 100],
    "mashort": [21, 50],
}
DEFAULT_PARAMS = {"malong": 200, "mashort": 21, "rsi_len": 3, "sl_pct": 0.01, "tp_pct": 0.01}


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


def _run(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ml = c.rolling(int(p["malong"])).mean()
    ms = c.ewm(span=int(p["mashort"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    lg = ((c > ml) & (c < ms) & (r < 20)).to_numpy()
    sh = ((c < ml) & (c > ms) & (r > 80)).to_numpy()
    xl = ((c > ms) & (c < lo.shift(1))).to_numpy()
    xs = ((c < ms) & (c > h.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov, hv, lv = bars_df["open"].to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - s_) or hv[i] >= ov[entry_i] * (1 + t_)):
            pos = 0
        if pos == 0 and i + 1 < m and lg[i]:
            le[i], pos, entry_i = True, 1, i + 1
        elif pos == 0 and i + 1 < m and sh[i]:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == 1 and i >= entry_i and xl[i]:
            lx[i], pos = True, 0
        elif pos == -1 and i >= entry_i and xs[i]:
            sx[i], pos = True, 0
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le = _run(bars_df, p)[0]
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["sl_pct"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp_pct"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
