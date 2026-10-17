"""Closes crossing the EMA 50 with RSI 14 on the same side of 50 and a moves-only "ADX" above 20, with a 2.5 ATR stop
and a 1.5 ATR target, 45-minute bars.
Port of FMZ strategy #482430 "多重指标动态跟踪趋势波段交易策略-Multi-Indicator-Dynamic-Trend-Following-Trading-Strategy" (EMA Momentum Scalper).

FMZ source id: 482430

Source
    https://www.fmz.com/strategy/482430 (PineScript v5, FMZ last modified 2025-02-18 14:02:44).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-167), ATR 14 (SL 2.5, TP 1.5), EMA 50, RSI 14, ADX 14 > 20
    diPlus = rma(max(high - high[1], 0), 14), diMinus = rma(max(low[1] - low, 0), 14) (no true-range scaling)
    adx = rma(100 |diPlus - diMinus| / (diPlus + diMinus), 14)
    crossover(close, ema) and rsi > 50 and adx > 20 -> entry long with exit(stop = close - 2.5 ATR,
    limit = close + 1.5 ATR, trail_points = 2.5 ATR); short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "ADX" is built from raw moves as written (scale-free ratio).
    * trail_points without trail_offset is inert (lane convention): no trail. The timeout input is never used.
    * The bracket is placed with the entry from the signal bar: 2.5 ATR / close and 1.5 ATR / close, shifted one bar
      inside stops() and re-based on the fill (house rule). Sizing methods and leverage are sizing (quoted).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "45min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, an EMA, RSI, a move-based ADX and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: capital-percent sizing and 15x leverage quoted; the bracket via stops(), in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482430_ema50_cross_rsi_move_adx_atr_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.5, 1.5],
    "tp_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"atr_len": 14, "sl_mult": 2.5, "tp_mult": 1.5, "ema_len": 50, "rsi_len": 14, "adx_len": 14,
                  "adx_min": 20.0}


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["adx_len"])
    dp = _rma((h - h.shift(1)).clip(lower=0), n)
    dm = _rma((lo.shift(1) - lo).clip(lower=0), n)
    adx = _rma(100 * (dp - dm).abs() / (dp + dm), n)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    strong = adx > p["adx_min"]
    long_e = ((c > ema) & (c.shift(1) <= ema.shift(1)) & (rsi > 50) & strong).astype(bool)
    short_e = ((c < ema) & (c.shift(1) >= ema.shift(1)) & (rsi < 50) & strong).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_mult"] * a, "tp_stop": p["tp_mult"] * a}


def portfolio_kwargs(**params):
    return {}
