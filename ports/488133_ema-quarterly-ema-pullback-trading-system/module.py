"""Close crossings back over the EMA 10 or EMA 21 with RSI 14 under 40, 1-minute bars, long only: a close 8 % over the EMA 10 or a close back under it closes, and a stop 15 % under the signal close cuts the loss.
Port of FMZ strategy #488133 "季度EMA动态回撤交易系统-Quarterly-EMA-Pullback-Trading-System" (Quarterly EMA Strategy).

FMZ source id: 488133

Source
    https://www.fmz.com/strategy/488133 (PineScript v5, FMZ last modified 2025-03-25 13:15:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 291-335), EMA 10 / 21; RSI 14 < 40; exit 8 % over EMA 10; stop 15 % under the entry close; 10 % of equity
    (crossover(close, ema10) or crossover(close, ema21)) and rsi < 40 -> entryPrice := close, entry Buy
    close > ema10 x 1.08 or crossunder(close, ema10) -> close Buy;  every bar: exit(stop = entryPrice x 0.85)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is 15 % under the signal close, sent as a fraction of the fill open (a level at or through
      it is marketable and closed one bar late, as #458256). A later signal while held moves entryPrice and
      so the stop; the port keeps the opening stop, mark trailing_stop_pending (as #434428). Long only.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent stop as a fraction of the fill.
    2 generic: PASS, EMA pullback re-crossings with RSI filter, EMA exits and a percent stop.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488133_ema10_21_recross_rsi40_ema_exits_stop15pct_long"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_max": [40, 30],
    "stop_pct": [15.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_max": 40, "stop_pct": 15.0, "jump_pct": 8.0}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    e10 = c.ewm(span=10, adjust=False).mean()
    e21 = c.ewm(span=21, adjust=False).mean()
    pc = c.shift(1)
    x10 = (c > e10) & (pc <= e10.shift(1))
    x21 = (c > e21) & (pc <= e21.shift(1))
    le = (x10 | x21) & (_rsi(c, 14) < float(p["rsi_max"]))
    lx = (c > e10 * (1 + float(p["jump_pct"]) / 100)) | ((c < e10) & (pc >= e10.shift(1)))
    sl = c * (1 - float(p["stop_pct"]) / 100)
    return le, lx, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, sl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    thr = lf & (sl.shift(1) >= o)    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return le, (lx | thr) & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, sl = _signals(bars_df, p)
    f = 1 - sl.shift(1) / bars_df["open"]
    return {"sl_stop": f.where(f > 0)}


def portfolio_kwargs(**params):
    return {}
