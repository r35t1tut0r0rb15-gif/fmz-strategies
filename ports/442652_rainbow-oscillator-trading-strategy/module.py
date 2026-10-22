"""Rainbow oscillator crossings (a weighted blend of CCI, RSI and stochastic over 16 and 22 bars, each double-RMA smoothed over 8): the slow line crossing under the fast line in a rising fast line goes long,
crossing over in a falling one goes short; a 5 % target and 2 % stop from the fill; reversing.
Port of FMZ strategy #442652 "Rainbow Oscillator Trading Strategy" (Rainbow Oscillator [Strategy]).

FMZ source id: 442652

Source
    https://www.fmz.com/strategy/442652 (PineScript v5, FMZ last modified 2024-02-23 14:57:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 133-266), weights 0.33 each; fast 16, slow 22; samples RMA 8 x 2; trend filter on; take profit 5 %, stop 2 %; margin 100, capital 2000; no backtest header
    magic(n) = 0.33 cci(close, n) + 0.33 (rsi(close, n) - 50) + 0.33 (stoch(close, high, low, n) - 50);  sampled = rma(rma(magic, 8), 8);  upTrend = fastS > fastS[1]
    buy = upTrend and crossunder(slowS, fastS) -> close Short, entry Long;  sell = not upTrend and crossover(slowS, fastS) -> close Long, entry Short;  exit(stop / limit = avg -+ 2 % / 5 %)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent every bar from the average (fill) price; on the flat signal bar it is na, so
      it is ported active from the fill bar (#440797) as fixed fractions 0.05 / 0.02 of the fill. The
      level bands only plot. ta.cci uses the mean absolute deviation. The source has no backtest header
      and names no bar size: FREQ = "bar_size_pending" (rule 1); precompute builds the bars with the
      house bar_sizes.build_bars(raw_1m_df, params["bar_size"]); the driver supplies bar_size (never in
      GRID / DEFAULT_PARAMS). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). The margin settings and capital are sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, blended oscillator crossings with a trend filter.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: margin settings and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_442652_rainbow_oscillator_cross_pct_bracket"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast_period": [16, 10],
    "slow_period": [22, 40],
}
DEFAULT_PARAMS = {"fast_period": 16, "slow_period": 22, "w1": 0.33, "w2": 0.33, "w3": 0.33, "sample_period": 8,
                  "tp_pct": 0.05, "sl_pct": 0.02}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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


def _cci(x, n):
    ma = x.rolling(n).mean()
    md = x.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    return (x - ma) / (0.015 * md)


def _magic(bars_df, n, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    return float(p["w2"]) * _cci(c, n) + float(p["w1"]) * (_rsi(c, n) - 50) + float(p["w3"]) * (st - 50)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sp = int(p["sample_period"])
    fs = _rma(_rma(_magic(bars_df, int(p["fast_period"]), p), sp), sp)
    ss = _rma(_rma(_magic(bars_df, int(p["slow_period"]), p), sp), sp)
    up = fs > fs.shift(1)
    lsig = (up & (ss < fs) & (ss.shift(1) >= fs.shift(1))).to_numpy()
    ssig = (~up & fs.shift(1).notna() & (ss > fs) & (ss.shift(1) <= fs.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
