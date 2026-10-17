"""EMA 40 breakdowns with expanding ATR, short only as written, from flat, with a 1.2 ATR stop and a 72-bar time exit,
1-hour bars: flat, with EMA 15 below EMA 40 and ATR above its 14-bar average, the close crossing below EMA 40 goes
short with a stop 1.2 ATR above the signal close; the trade closes 72 bars after the last signal.
Port of FMZ strategy #488020 "多指标确认动态追踪突破量化交易策略-Multi-Indicator-Confirmation-Dynamic-Trailing-Breakout-Quantitative-Trading-Strategy" (MomentumBreakout V1.2 - DOGE/USDT).

FMZ source id: 488020

Source
    https://www.fmz.com/strategy/488020 (PineScript v6, FMZ last modified 2025-03-24 14:20:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 235-308), EMA 15 / 40, ATR 14, RSI 14, MACD 12 / 26 / 9, max hold 72 bars
    [macdLine_1h, signalLine_1h, _] = request.security("60", ta.macd(...)); macdLine_1h := macdLine_1h[1] (same for
    the signal); trendUp_1h = emaFast > emaSlow and rsi_1h > 50 and macdLine_1h > signalLine_1h
    breakoutLong = crossover(close, emaFast) and trendUp_1h and close > sma(close, 20)
    breakoutShort = crossunder(close, emaSlow) and emaFast < emaSlow and atr > sma(atr, 14)
    a signal sets entryBarIndex; position != 0 and bar_index - entryBarIndex >= 72 -> close_all
    signal and flat -> entry + exit(stop = close -+ 1.2 ATR) (placed once, with the entry)

Interpretation choices (Pine rules in SURVEY_README.md)
    * macdLine_1h := macdLine_1h[1] reassigns each variable to its own previous value, which starts na on the first bar
      and so stays na: trendUp_1h is never true and breakoutLong never fires. As written the strategy trades short
      only; the long side is not emitted.
    * The stop variable ratchets while short, but strategy.exit is called only with the entry: the stop stays at the
      signal bar's 1.2 ATR, re-based on the fill (sl_stop, shifted one bar inside stops()). Exact, no mark.
    * Entries only from flat: simulate() mirrors the stop from the fill bar (#430254); the time exit counts from the
      last signal bar (also signals while held) and is a close-based exit signal (rule 3). Opposite entries cannot
      occur.
    * The leverage-based quantity is sizing (quoted). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the
      backtest header. "DOGE/USDT" in the title is a label.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at the signal bar.
    2 generic: PASS, EMAs, ATR and bar counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk / leverage quantity quoted; the stop ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_488020_ema40_breakdown_atr_time_exit"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.2, 2.0],
    "max_hold": [72, 36],
}
DEFAULT_PARAMS = {"ema_fast": 15, "ema_slow": 40, "atr_len": 14, "sl_atr": 1.2, "max_hold": 72}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _sl_frac(bars_df, p):
    return p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    atr = _atr(bars_df, int(p["atr_len"]))
    sig = ((c < es) & (c.shift(1) >= es.shift(1)) & (ef < es) & (atr > atr.rolling(14).mean())).to_numpy()
    sl_f = _sl_frac(bars_df, p).to_numpy(dtype=float)
    ov, hv = bars_df["open"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    hold = int(p["max_hold"])
    m = len(c)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill_i, s_, last_sig = 0, -1, np.nan, -10 ** 9
    for i in range(m):
        if pos == -1 and i >= fill_i and hv[i] >= ov[fill_i] * (1 + s_):   # the house stop from the fill price
            pos = 0
        if sig[i]:
            last_sig = i
        if pos != 0 and i - last_sig >= hold:
            pos, sx[i] = 0, True
        elif pos == 0 and sig[i]:
            pos, fill_i, s_, se[i] = -1, i + 1, sl_f[i], True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return false, false.copy(), pd.Series(se, index=idx), pd.Series(sx, index=idx)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _sl_frac(bars_df, p).shift(1)}


def portfolio_kwargs(**params):
    return {}
