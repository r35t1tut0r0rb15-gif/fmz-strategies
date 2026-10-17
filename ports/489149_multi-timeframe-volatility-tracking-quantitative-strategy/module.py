"""EMA 3 / 8 cross-ups above EMA 55, spaced 72 bars apart, from flat, with an ATR bracket, long only, 1-minute bars:
EMA 3 crossing above EMA 8 with the close above EMA 55, at least 72 bars after the last entry and with no position
open, goes long with a stop 1.2 ATR and a target 2 ATR away.
Port of FMZ strategy #489149 "多周期波动跟踪量化策略-Multi-Timeframe-Volatility-Tracking-Quantitative-Strategy" (DOGE/USDT 5X Scalping Strategy).

FMZ source id: 489149

Source
    https://www.fmz.com/strategy/489149 (PineScript v6, FMZ last modified 2025-04-02 10:50:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 169-234), EMA 3 / 8 / 55, ATR 14, 72 bars between trades, SL 1.2 ATR, TP 2 ATR
    valid = crossover(ema3, ema8) and close > ema55 and bar_index - lastTradeBar >= 72 and position == 0
    -> entry long + exit(stop = close - 1.2 ATR, limit = close + 2 ATR); lastTradeBar = bar_index

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is placed once, on the signal bar: sl_stop = 1.2 x ATR / close, tp_stop = 2 x ATR / close, shifted
      one bar inside stops(), re-based on the fill (house rule).
    * Entries only from flat: simulate() follows the house bracket on bars (from the fill bar), as the desktop's
      flat-only bracket ports; the 72-bar spacing counts from the signal bar (lastTradeBar starts at 0, as written).
      Long only.
    * The 5x leverage and the risk-based quantity are sizing. Stop module: portfolio_kwargs {} (D4). FREQ = "1min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: PASS, EMAs and ATR multiples.
    3 crypto-exchange-only: no ("DOGE/USDT" in the title and the exchange pair only).
    4 signals only: leverage and the 1 %-risk quantity quoted; the bracket ported via stops() and quoted.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489149_ema_3_8_cross_spaced_atr_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trade_interval": [72, 30],
    "tp_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 3, "slow": 8, "trend": 55, "atr_period": 14, "trade_interval": 72, "sl_mult": 1.2,
                  "tp_mult": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    et = c.ewm(span=int(p["trend"]), adjust=False).mean()
    sig = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (c > et)).to_numpy()
    frac = (_atr(bars_df, int(p["atr_period"])) / c).to_numpy(dtype=float)
    sl_f, tp_f = p["sl_mult"] * frac, p["tp_mult"] * frac
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_, last = 0, -1, np.nan, np.nan, 0
    gap = int(p["trade_interval"])
    for i in range(m):
        if pos != 0 and 0 <= entry_i <= i:               # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_):
                pos = 0
        if pos == 0 and sig[i] and i - last >= gap and not np.isnan(sl_f[i]) and i + 1 < m:
            le[i], pos, entry_i, s_, t_, last = True, 1, i + 1, sl_f[i], tp_f[i], i
    return le


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(_run(bars_df, p), index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_period"])) / bars_df["close"]
    return {"sl_stop": (p["sl_mult"] * frac).shift(1), "tp_stop": (p["tp_mult"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
