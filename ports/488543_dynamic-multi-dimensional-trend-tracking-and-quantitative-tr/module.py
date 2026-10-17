"""SuperTrend (7, 0.8) direction with an EMA 9 and RSI filter and a 1 % / 3 ATR bracket, 3-minute bars: with the Pine
SuperTrend direction equal to 1 (a down-trend in Pine's convention, as written), the close above EMA 9 and RSI 14
above 40 the strategy goes long; with direction -1, the close below EMA 9 and RSI below 60 it goes short; each trade
has a 1 % stop and a 3 ATR target.
Port of FMZ strategy #488543 "动态多维度趋势追踪与量化交易策略-Dynamic-Multi-Dimensional-Trend-Tracking-and-Quantitative-Trading-Strategy" (SOL Scalper - Supertrend + EMA + RSI (One Position at a Time)).

FMZ source id: 488543

Source
    https://www.fmz.com/strategy/488543 (PineScript v6, FMZ last modified 2025-03-28 17:31:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 110-156), ATR 7, SuperTrend factor 0.8, EMA 9, RSI 14 (40 / 60), SL 1 %, TP 3 ATR
    long = direction == 1 and close > ema and rsi > 40;  short = direction == -1 and close < ema and rsi < 60
    not inPosition: entry + exit(stop = close -+ 1 %, limit = close +- 3 ATR); inPosition = true
    position == 0 -> inPosition = false

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend's direction is 1 in a down-trend and -1 in an up-trend (Pine); the source's tests are kept as
      written.
    * inPosition is cleared at the end of the signal bar itself (the position fills only at the next open), so the
      gate never blocks: every condition bar is an entry (a same-side one is ignored while held) and re-places the
      bracket: mark trailing_stop_pending; the port keeps the entry's bracket (sl_stop 1 %, tp_stop = 3 x ATR / close of
      the signal bar, shifted one bar inside stops(), re-based on the fill).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "3min" from the backtest
      header. "SOL" in the title is a label.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, SuperTrend, EMA, RSI, a percentage and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488543_supertrend_dir_ema_rsi_bracket"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "st_factor": [0.8, 2.0],
    "tp_mult": [3.0, 1.5],
}
DEFAULT_PARAMS = {"atr_len": 7, "st_factor": 0.8, "ema_len": 9, "rsi_len": 14, "sl_pct": 1.0, "tp_mult": 3.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _pine_st_direction(bars_df, factor, n):
    """ta.supertrend direction: 1 = down-trend (line on the upper band), -1 = up-trend; 0 before the ATR exists."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    d_out = np.zeros(m, dtype=np.int8)
    pu = pl = 0.0
    prev_st = np.nan
    for i in range(m):
        if np.isnan(atr[i]):
            pu = pl = 0.0
            continue
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        if i > 0:
            lw = lw if (lw > pl or c[i - 1] < pl) else pl
            up = up if (up < pu or c[i - 1] > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        prev_st = lw if d == -1 else up
        pu, pl = up, lw
        d_out[i] = d
    return d_out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = _pine_st_direction(bars_df, float(p["st_factor"]), int(p["atr_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((d == 1) & (c > ema) & (rsi > 40)).astype(bool)
    short_e = ((d == -1) & (c < ema) & (rsi < 60)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    tp = (p["tp_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
