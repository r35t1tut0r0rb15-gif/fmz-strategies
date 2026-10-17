"""EMA 10 / WMA 20 crosses from flat with a tick bracket, 30-minute bars: the EMA crossing above the WMA while flat goes
long, crossing below goes short; the stop (200 ticks) and the second target (400 ticks) from the signal close become
ATR fractions. The half-size first target is sizing, not ported.
Port of FMZ strategy #432112 "Dual Take Profit Moving Average Crossover Quantitative Strategy" (FS ATR & PS (MA)).

FMZ source id: 432112

Source
    https://www.fmz.com/strategy/432112 (PineScript v4, FMZ last modified 2023-11-14 16:04:33).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 185-242), EMA 10 / WMA 20, a = 20 x 10 ticks, b = 40 x 10 ticks, size 1
    crossover(ema10, wma20) and position_size == 0 -> entry long;  crossunder and flat -> entry short
    exit1(stop = close - a ticks, limit = close + a ticks, qty = size / 2);  exit2(stop = close - a ticks, limit = close + b ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: a = 200 and b = 400 ticks (20 / 40 USD on BTC_USDT, mintick 0.1) become sl_atr /
      tp_atr x the Wilder ATR 14 of the signal bar as fractions of its close (about 0.13 / 0.27 ATR
      on 30-minute BTC), shifted one bar inside stops() and re-based on the fill.
    * Exit1 closes half the position at the nearer target: a quantity split, criterion 4, quoted in
      original_sizing.txt. The port carries the full position to Exit2's levels (the shared stop and
      the farther target). The "even level" is plotted only.
    * Entries only from flat (position_size == 0 at the signal bar): the port's own state machine
      follows the house bracket on bars (an entry may follow a bracket exit in the same bar, as Pine's
      flat position at that close allows), so Opposite entries cannot occur. The date inputs (from
      2019, no end) are the author's backtest window: dropped. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: size 1, the risk input and the half-size first target stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432112_ema_wma_cross_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.13, 1.0],
    "tp_atr": [0.27, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 10, "wma_len": 20, "atr_len": 14, "sl_atr": 0.13, "tp_atr": 0.27}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: float(np.dot(a, w) / w.sum()), raw=True)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    w = _wma(c, int(p["wma_len"]))
    up = ((e > w) & (e.shift(1) <= w.shift(1))).to_numpy()
    dn = ((e < w) & (e.shift(1) >= w.shift(1))).to_numpy()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    ks, kt = float(p["sl_atr"]), float(p["tp_atr"])
    m = len(ov)
    tgt = np.zeros(m, dtype=np.int8)
    ent = np.zeros(m, dtype=np.int8)
    sl_arr, tp_arr = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i, sl, tp = 0, -1, 0.0, 0.0
    for i in range(m):
        if pos != 0 and i >= e_i:                        # house bracket from the fill price
            ep = ov[e_i]
            if pos == 1 and (lv[i] <= ep * (1 - sl) or hv[i] >= ep * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= ep * (1 + sl) or lv[i] <= ep * (1 - tp)):
                pos = 0
        if pos == 0 and not np.isnan(af[i]) and (up[i] or dn[i]):
            pos = 1 if up[i] else -1
            e_i, sl, tp = i + 1, af[i] * ks, af[i] * kt
            sl_arr[i], tp_arr[i] = sl, tp
            ent[i] = pos
        tgt[i] = pos
    return tgt, ent, sl_arr, tp_arr


def _emit(tgt, ent, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1                                       # an entry may follow a bracket exit in the same bar
    lx = (prev == 1) & (tgt == 0)
    se = ent == -1
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tgt, ent, _, _ = _run(bars_df, p)
    return _emit(tgt, ent, bars_df.index)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl_arr, tp_arr = _run(bars_df, p)
    idx = bars_df.index
    return {"sl_stop": pd.Series(sl_arr, index=idx).shift(1), "tp_stop": pd.Series(tp_arr, index=idx).shift(1)}


def portfolio_kwargs(**params):
    return {}
