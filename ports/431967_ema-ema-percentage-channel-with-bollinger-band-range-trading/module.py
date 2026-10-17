"""Range trading inside a +-1 % EMA 200 channel (mdeacey), 3-minute bars: the close crossing back above the lower Bollinger
band (20, 2) inside the channel goes long, back below the upper band goes short, each with the opposite band as the target
and an ATR-band stop; the close leaving the channel on the far side closes the position.
Port of FMZ strategy #431967 "EMA百分比通道与布林带区间交易策略EMA-Percentage-Channel-with-Bollinger-Band-Range-Trading-Strategy" ([mdeacey] EMA% Channel + BB Range Strategy).

FMZ source id: 431967

Source
    https://www.fmz.com/strategy/431967 (PineScript v4, FMZ last modified 2023-11-13 17:38:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 179-239), EMA 200 +-1 %, BB 20 / 2, ATR 14 x 1.75 (own rma)
    crossover(close, lower) and lowerbande < close < upperbande -> entry long;  crossunder(close, lowerbande) -> close long
    crossunder(close, upper) and inside the channel -> entry short;  crossover(close, upperbande) -> close short
    exit long: limit = upper, stop = low - rma(1.75 tr, 14) re-issued every bar (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit levels are re-issued every bar at the current band and the current bar's low - ATR (a
      moving level): rule 2, mark trailing_stop_pending; the port fixes them at the signal bar's
      values, as fractions of its close, shifted one bar. The ATR is the source's own rma (seeded from
      0, as written).
    * The closes act on the position held at the bar's start and do not undo a reversal. "Flat"
      follows the house bracket on bars. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). stdev is the population deviation. FREQ = "3min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (rule 2).
    2 generic: PASS, an EMA percentage channel, Bollinger bands and an ATR band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_431967_ema_channel_bb_range"
FAMILY = "bollinger_reversion"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "channel_pct": [1.0, 2.0],
    "atr_mult": [1.75, 3.0],
}
DEFAULT_PARAMS = {"ema_len": 200, "channel_pct": 1.0, "length": 20, "mult": 2.0, "atr_len": 14, "atr_mult": 1.75}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    ue, le_ = e * (1 + p["channel_pct"] / 100), e * (1 - p["channel_pct"] / 100)
    n = int(p["length"])
    ma, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    up, dn = ma + p["mult"] * sd, ma - p["mult"] * sd
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).to_numpy()
    y = int(p["atr_len"])
    band = np.zeros(len(tr))
    s = 0.0
    for i in range(len(tr)):
        x = tr[i] * float(p["atr_mult"])
        s = (x + (y - 1) * s) / y if not np.isnan(x) else np.nan
        band[i] = s
        s = 0.0 if np.isnan(s) else s

    def xo(a, b):
        return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()
    inside = ((c < ue) & (c > le_)).to_numpy()
    el, es = xo(c, dn) & inside, xo(up, c) & inside
    xl, xs = xo(le_, c), xo(c, ue)
    ov, hv, lv, cv = (x.to_numpy(dtype=float) for x in (o, h, lo, c))
    upv, dnv = up.to_numpy(), dn.to_numpy()
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - s_) or hv[i] >= ep * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + s_) or lv[i] <= ep * (1 - t_)):
                pos = 0
        start = pos
        new = 0
        if el[i]:
            new, pos = 1, 1
        if xl[i] and start == 1 and pos == 1:
            pos = 0
        if es[i]:
            new, pos = -1, -1
        if xs[i] and start == -1 and pos == -1:
            pos = 0
        if pos == new and new != 0 and start != new:
            if new == 1:
                s_, t_ = (cv[i] - (lv[i] - band[i])) / cv[i], (upv[i] - cv[i]) / cv[i]
            else:
                s_, t_ = ((hv[i] + band[i]) - cv[i]) / cv[i], (cv[i] - dnv[i]) / cv[i]
            s_, t_ = max(s_, 1e-9), max(t_, 1e-9)
            e_i = i + 1
            sl_arr[i], tp_arr[i] = s_, t_
        tgt[i] = pos
    return tgt, sl_arr, tp_arr


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
    tgt, _, _ = _run(bars_df, p)
    return _emit(tgt, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
