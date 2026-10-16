"""Three SMMAs + Williams fractal + RSI, 3-hour bars: after SMMA 21 crosses above SMMA 50 (and until any
SMMA turns down), the first bar with its low above SMMA 21, RSI 14 at or above 50 and a down fractal or
a close crossing above SMMA 200 goes long (from flat); the mirror goes short. Each trade has a 0.1 %
stop and a 0.4 % target.
Port of FMZ strategy #428052 "Triple Moving Average Crossover and Williams Indicator Strategy".

FMZ source id: 428052

Source
    https://www.fmz.com/strategy/428052 (PineScript v5, FMZ last modified 2023-09-28 10:58:16).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 174-300), SMMA 21 / 50 / 200, RSI 14, fractal periods 2, SL 0.1 %, TP 0.4 %
    smma = rma seeded by the SMA; waitingUp := crossover(fast, mid) ? true : any SMMA falling ? false : held
    long = low > fast and rsi >= 50 and (downFractal or crossover(close, slow)) and waitingUp and flat
    after an entry waitingUp := false; short mirrors
    exit(stop = avg x (1 -+ 0.1 %), limit = avg x (1 +- 0.4 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Fractals as the source's loop (Williams fractal with up to four equal bars before the pivot,
      pivot n bars back, confirmed n bars after it): no look-ahead.
    * "Flat" follows the house bracket: the loop marks the position closed once a bar's high / low
      reaches the stop or target from the fill price (next open). barstate.isconfirmed is true on history.
    * Percent-of-entry levels: sl_stop 0.001, tp_stop 0.004.
    * Stop module: portfolio_kwargs {} (driver D4). Opposite entries cannot occur (entries from flat).
    * Stops on 3-hour bars: mark coarse_bar_stop. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, MA lengths, RSI level, percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored; exits quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428052_three_smma_fractal_rsi"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "n": [2, 3],
    "stop_loss": [0.1, 0.5],
    "target_profit": [0.4, 1.0],
}
DEFAULT_PARAMS = {"fast": 21, "mid": 50, "slow": 200, "rsi_len": 14, "n": 2,
                  "stop_loss": 0.1, "target_profit": 0.4}


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


def _fractals(h, lo, n):
    H = lambda k: h.shift(k)
    L = lambda k: lo.shift(k)
    up_after = np.logical_and.reduce([H(n - i) < H(n) for i in range(1, n + 1)])
    dn_after = np.logical_and.reduce([L(n - i) > L(n) for i in range(1, n + 1)])
    up_before = np.zeros(len(h), dtype=bool)
    dn_before = np.zeros(len(h), dtype=bool)
    for k in range(5):
        u = np.ones(len(h), dtype=bool)
        d = np.ones(len(h), dtype=bool)
        for j in range(1, k + 1):
            u &= (H(n + j) <= H(n)).to_numpy()
            d &= (L(n + j) >= L(n)).to_numpy()
        for i in range(1, n + 1):
            u &= (H(n + i + k) < H(n)).to_numpy()
            d &= (L(n + i + k) > L(n)).to_numpy()
        up_before |= u
        dn_before |= d
    return np.asarray(up_after) & up_before, np.asarray(dn_after) & dn_before


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    up_f, dn_f = _fractals(h, lo, int(p["n"]))
    d = c.diff()
    k = int(p["rsi_len"])
    ru, rd = _rma(d.clip(lower=0), k), _rma(-d.clip(upper=0), k)
    rsi = (100 - 100 / (1 + ru / rd)).where(ru != 0, 0.0).where(rd != 0, 100.0)
    rsi_hi = (rsi >= 50).to_numpy()
    rsi_ok = rsi.notna().to_numpy()
    fs, ms, ss = _rma(c, int(p["fast"])), _rma(c, int(p["mid"])), _rma(c, int(p["slow"]))
    rise = lambda x: (x > x.shift(1)).to_numpy()
    fall = lambda x: (x < x.shift(1)).to_numpy()
    any_fall = fall(fs) | fall(ms) | fall(ss)
    any_rise = rise(fs) | rise(ms) | rise(ss)
    x_up = ((fs > ms) & (fs.shift(1) <= ms.shift(1))).to_numpy()
    x_dn = ((fs < ms) & (fs.shift(1) >= ms.shift(1))).to_numpy()
    px_up = ((c > ss) & (c.shift(1) <= ss.shift(1))).to_numpy()
    px_dn = ((c < ss) & (c.shift(1) >= ss.shift(1))).to_numpy()
    ov, hv, lv, fv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float), fs.to_numpy()
    sl, tp = p["stop_loss"] / 100, p["target_profit"] / 100
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    w_up = w_dn = False
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + sl) or lv[i] <= e * (1 - tp)):
                pos = 0
        w_up = True if x_up[i] else (False if any_fall[i] else w_up)
        w_dn = True if x_dn[i] else (False if any_rise[i] else w_dn)
        if pos == 0 and rsi_ok[i] and lv[i] > fv[i] and rsi_hi[i] and (dn_f[i] or px_up[i]) and w_up:
            le[i] = True
            w_up = False
            pos, entry_i = 1, i + 1
        if pos == 0 and rsi_ok[i] and hv[i] < fv[i] and not rsi_hi[i] and (up_f[i] or px_dn[i]) and w_dn:
            se[i] = True
            w_dn = False
            pos, entry_i = -1, i + 1
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_loss"]) / 100, "tp_stop": float(p["target_profit"]) / 100}


def portfolio_kwargs(**params):
    return {}
