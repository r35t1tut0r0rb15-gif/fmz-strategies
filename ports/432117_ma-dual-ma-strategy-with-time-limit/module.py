"""EMA 14 / 21 of the open, always flipping, 45-minute bars: the fast EMA turning at or above the slow one goes long, turning
below goes short; a 200-tick stop and a 1000-tick target become ATR fractions. The 200-point trail has no offset and is
not emitted.
Port of FMZ strategy #432117 "双MA时间限制交易策略Dual-MA-Strategy-with-Time-Limit" (Strategy Code Example (JayRogers time limiter)).

FMZ source id: 432117

Source
    https://www.fmz.com/strategy/432117 (PineScript v2, FMZ last modified 2023-11-14 16:45:03).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 141-218), EMA 14 / 21 of open, TP 1000, SL 200, trail 200 / offset 0 (ticks)
    dir = ema(open, 14) >= ema(open, 21)
    not dir[1] and dir -> entry long, close short;  dir[1] and not dir -> entry short, close long
    exit(profit = 1000, loss = 200, trail_points = 200, trail_offset = na) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: loss = 200 and profit = 1000 ticks (20 / 100 USD on BTC_USDT, mintick 0.1) become
      sl_atr / tp_atr x the Wilder ATR 14 of the signal bar as fractions of its close (about 0.1 /
      0.5 ATR on 45-minute BTC), shifted one bar inside stops() and re-based on the fill.
    * trail_points = 200 with trail_offset = na (an input below 1 is set to na by the source): Pine
      needs both to arm a trail, so as written it may never arm. Rule 2, mark trailing_stop_pending,
      not emitted (as #431396).
    * The start-time limiter (from 2016-05-01) is the author's backtest window: dropped; tradeInvert
      (false) is not used. A close of one side written after the other side's entry does not undo
      the reversal: REVERSAL INTENDED. After a bracket exit the port waits for the next flip (its
      state machine follows the house bracket on bars). Stop module: portfolio_kwargs {} (driver D4).
      FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the exits are ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_432117_open_ema_flip_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.1, 1.0],
    "tp_atr": [0.5, 3.0],
}
DEFAULT_PARAMS = {"fast": 14, "slow": 21, "atr_len": 14, "sl_atr": 0.1, "tp_atr": 0.5}


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
    f = o.ewm(span=int(p["fast"]), adjust=False).mean()
    s = o.ewm(span=int(p["slow"]), adjust=False).mean()
    d = (f >= s).to_numpy()
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
        if i >= 1 and not np.isnan(af[i]) and d[i] != d[i - 1]:
            new = 1 if d[i] else -1
            if new != pos:
                pos, e_i, sl, tp = new, i + 1, af[i] * ks, af[i] * kt
                sl_arr[i], tp_arr[i] = sl, tp
                ent[i] = pos
        tgt[i] = pos
    return tgt, ent, sl_arr, tp_arr


def _emit(tgt, ent, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = ent == 1
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
