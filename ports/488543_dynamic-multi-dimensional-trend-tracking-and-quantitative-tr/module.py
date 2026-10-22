"""SuperTrend 0.8 / 7 direction (long while direction is 1, the down-trend, as written) with the close beyond the EMA 9 and RSI 14 over 40 (under 60), 3-minute bars: the long state goes long, the short state goes short, each with a 1 % stop and a 3 ATR 7 target from the signal close; reversing.
Port of FMZ strategy #488543 "Dynamic Multi Dimensional Trend Tracking and Quantitative Trading Strategy" (SOL Scalper - Supertrend + EMA + RSI (One Position at a Time)).

FMZ source id: 488543

Source
    https://www.fmz.com/strategy/488543 (PineScript v6, FMZ last modified 2025-03-28 17:31:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-176), SuperTrend 0.8 / 7; EMA 9; RSI 14 / 40 / 60; SL 1 %; TP 3 ATR; capital 1000, 10 % of equity, commission 0.075 %
    not inPosition and direction == 1 and close > ema9 and rsi > 40 -> entry Long + exit(stop = close x 0.99, limit = close + 3 atr), inPosition := true
    not inPosition and direction == -1 and close < ema9 and rsi < 60 -> entry Short + mirror
    position == 0 -> inPosition := false (same bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is 1 in a down-trend, so the long side trades down-trends, as written. The
      inPosition flag is cleared on the same bar it is set (the position is still flat until the next
      open), so it never blocks: the conditions are states that repeat while held, each re-sending the
      bracket from the new close; the port keeps the opening levels, mark trailing_stop_pending (as
      #434428). The bracket is sent as fractions of the fill open (a level at or through it is marketable
      and closed one bar late, as #458256). An entry on the other side reverses (REVERSAL INTENDED). Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent / ATR bracket as fractions of the fill.
    2 generic: PASS, SuperTrend direction with EMA / RSI filters.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: capital 1000, 10 % of equity, commission 0.075 % stored, not ported.
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

NAME = "fmz_488543_supertrend08_7_dir_ema9_rsi_pct_atr_bracket_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrMultiplier": [0.8, 2.0],
    "tpMultiplier": [3.0, 1.5],
}
DEFAULT_PARAMS = {"atrMultiplier": 0.8, "tpMultiplier": 3.0, "atrLength": 7, "emaLength": 9, "rsiLength": 14,
                  "slPercent": 1.0}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["atrLength"])
    _, d = _supertrend(bars_df, float(p["atrMultiplier"]), n)
    e = c.ewm(span=int(p["emaLength"]), adjust=False).mean()
    r = _rsi(c, int(p["rsiLength"]))
    le = (d == 1) & (c > e) & (r > 40)
    se = (d == -1) & (c < e) & (r < 60)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    tp = _rma(tr, n) * float(p["tpMultiplier"])
    sl = c * float(p["slPercent"]) / 100
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
    return le & ~se, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
