"""EMA ribbon trends with RSI and stochastic filters, hourly bars, entries only from flat: EMA 8 > 13 > 21 > 34 > 55 with RSI 40-70 and stochastic K under 80 buys, with a 2 ATR stop and 4 ATR target from the signal close; EMA 13 under EMA 55, RSI over 70 or K over 95 closes it; the mirror sells.
Port of FMZ strategy #474022 "Multi EMA Trend Momentum Trading Strategy with Risk Management System" (Combined Strategy (Modernized)).

FMZ source id: 474022

Source
    https://www.fmz.com/strategy/474022 (PineScript v5, FMZ last modified 2024-12-05 14:52:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 92-176), EMA 8 / 13 / 21 / 34 / 55; RSI 14; stochastic 14; ATR 14: stop 2 x, target 4 x, trail_offset 1.5 x (no trail_points); size by 1 % risk
    ribbon up and 40 < rsi < 70 and k < 80 and flat -> entry LONG, exit(stop = close - 2 atr, limit = close + 4 atr, trail_offset = 1.5 atr);  long and (ema13 < ema55 or rsi > 70 or k > 95) -> close LONG;  short mirror (rsi 30-60, k > 20; exits ema13 > ema55, rsi < 30, k < 5)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_offset without trail_points sets no trail (as #441084). The bracket is sent once, on the
      signal bar, from its close and ATR; entries only from flat: a loop follows each trade's bracket on
      the bar's high / low and the close tests, so the flat gate lines up (as 449508); the levels are
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late). The two ribbons cannot hold on one bar. Opposite entries cannot occur. The risk-based size
      is not ported. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, EMA ribbon trends with oscillator filters, bracket and close exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based size from equity stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_474022_ema_ribbon_rsi_stoch_atr_bracket_from_flat"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {}


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
    e8, e13, e21, e34, e55 = (c.ewm(span=n, adjust=False).mean() for n in (8, 13, 21, 34, 55))
    r = _rsi(c, 14)
    hh, ll = h.rolling(14).max(), lo.rolling(14).min()
    k = 100 * (c - ll) / (hh - ll)
    lc = ((e8 > e13) & (e13 > e21) & (e21 > e34) & (e34 > e55) & (r < 70) & (r > 40) & (k < 80)).to_numpy()
    sc = ((e8 < e13) & (e13 < e21) & (e21 < e34) & (e34 < e55) & (r > 30) & (r < 60) & (k > 20)).to_numpy()
    xl = ((e13 < e55) | (r > 70) | (k > 95)).to_numpy()
    xs = ((e13 > e55) | (r < 30) | (k < 5)).to_numpy()
    atr = _atr(bars_df, 14).to_numpy(dtype=float)
    ov, hv, lv, cv = (z.to_numpy(dtype=float) for z in (o, h, lo, c))
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, tp_sent, side = np.full(m, np.nan), np.full(m, np.nan), np.zeros(m)
    pos, pend, sl, tp, sl_n, tp_n = 0, 0, np.nan, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, sl, tp = pend, 0, sl_n, tp_n
            through = (sl >= ov[i] or tp <= ov[i]) if pos == 1 else (sl <= ov[i] or tp >= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl, tp = 2, np.nan, np.nan
        elif pend in (2, 3):
            pos, pend, sl, tp = 0, 0, np.nan, np.nan
        if pos == 1 and (lv[i] <= sl or hv[i] >= tp):
            pos, sl, tp = 0, np.nan, np.nan      # the bracket fills inside this bar
        elif pos == -1 and (hv[i] >= sl or lv[i] <= tp):
            pos, sl, tp = 0, np.nan, np.nan
        if pend != 0:
            continue
        if pos == 0 and lc[i]:
            sl_n, tp_n = cv[i] - 2 * atr[i], cv[i] + 4 * atr[i]
            le[i], pend, sl_sent[i], tp_sent[i], side[i] = True, 1, sl_n, tp_n, 1
        elif pos == 1 and xl[i]:
            lx[i], pend = True, 3                # the close test: flat from the next open
        elif pos == 0 and sc[i]:
            sl_n, tp_n = cv[i] + 2 * atr[i], cv[i] - 4 * atr[i]
            se[i], pend, sl_sent[i], tp_sent[i], side[i] = True, -1, sl_n, tp_n, -1
        elif pos == -1 and xs[i]:
            sx[i], pend = True, 3
    ix = bars_df.index
    return [pd.Series(z, index=ix) for z in (le, lx, se, sx, sl_sent, tp_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, tp_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, tp_l, sd = sl_l.shift(1), tp_l.shift(1), sd.shift(1)    # the signal bar's levels, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    tp_f = (tp_l / o - 1).where(sd > 0, 1 - tp_l / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
