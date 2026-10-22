"""SMA 20 / 50 crossings filtered by the RSI 14 rounded to 0 or 1, 15-minute bars: the cross up with the RSI at 50 or over goes long, the cross down with it under 50 goes short; a long closes on the next cross up while held, a short on the next cross down; each new entry's stop is 2 ATR from the average price of the position it replaces.
Port of FMZ strategy #468309 "Dynamic Trend Following Strategy with Machine Learning Enhanced Risk Management" (Enhanced Trend Following with ML).

FMZ source id: 468309

Source
    https://www.fmz.com/strategy/468309 (PineScript v5, FMZ last modified 2024-09-26 14:58:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-177), SMA 20 / 50; "ML" signal = round(rsi(14) / 100); ATR 14 x 2 stop from strategy.position_avg_price on the signal bar; trailing stops start at na
    crossover and round(rsi / 100) > 0.5 -> entry Long + exit(stop = avg - 2 atr);  crossunder and round(rsi / 100) < 0.5 -> entry Short + exit(stop = avg + 2 atr)
    long and crossover -> close Long;  short and crossunder -> close Short;  trail stops = min / max(na, close) (stay na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ML confidence" is the RSI rounded to 0 or 1, so the filters are RSI >= 50 / < 50. The stop
      is sent on the signal bar from strategy.position_avg_price, which is still the price of the
      position held then: na from flat (no stop), and the replaced position's fill price on a reversal,
      as written. The loop tracks those fill prices; the stop is sent as a fraction of the new fill open
      (a level at or through it is marketable and is sent as a bar-close exit on the fill bar, one bar
      late). The trailing stops start at na (var of the first bar's average price) and math.min / max
      keeps them na, so they never act. The closes follow the entries and act only on a position held
      into the bar and not being reversed. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver
      D4). No sizing code. FREQ = "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the stop base, as written.
    2 generic: PASS, SMA crossings with an RSI half filter.
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

NAME = "fmz_468309_sma20_50_cross_rsi_half_filter_prev_avg_atr_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [20, 10],
    "long_len": [50, 100],
    "sl_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"short_len": 20, "long_len": 50, "sl_mult": 2.0, "atr_len": 14}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    a, b = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    xo = ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    xu = ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()
    ml = np.round(_rsi(c, 14).to_numpy() / 100)
    with np.errstate(invalid="ignore"):
        lc, sc = xo & (ml > 0.5), xu & (ml < 0.5)
    dist = (float(p["sl_mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sent, side = np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, active, lvl = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, active = pend, 0, ov[i], lvl
            if (pos == 1 and active >= ov[i]) or (pos == -1 and active <= ov[i]):
                if pos == 1:
                    lx[i] = True                 # stop through the fill: closed at the next open
                else:
                    sx[i] = True
                pend, active = 2, np.nan
        elif pend == 2:
            pos, pend, avg, active = 0, 0, np.nan, np.nan
        if (pos == 1 and lv[i] <= active) or (pos == -1 and hv[i] >= active):
            pos, avg, active = 0, np.nan, np.nan  # the stop fills inside this bar
        if pend == 2:
            continue
        cur = pos
        if lc[i] and pos != 1:
            cur, lvl = 1, avg - dist[i]          # na when flat
        if sc[i] and pos != -1:
            cur, lvl = -1, avg + dist[i]
        if pos == 1 and xo[i] and cur == 1:
            cur = 0                              # the close acts only on a long held, not reversed
        if pos == -1 and xu[i] and cur == -1:
            cur = 0
        if cur == 1 and pos != 1:
            le[i], pend, sent[i], side[i] = True, 1, lvl, 1
        elif cur == -1 and pos != -1:
            se[i], pend, sent[i], side[i] = True, -1, lvl, -1
        elif cur == 0 and pos == 1:
            lx[i], pend = True, 2
        elif cur == 0 and pos == -1:
            sx[i], pend = True, 2
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lvl, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    l1, s1 = lvl.shift(1), sd.shift(1)                         # the signal bar's level, read at the fill
    f = (1 - l1 / o).where(s1 > 0, l1 / o - 1)
    return {"sl_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
