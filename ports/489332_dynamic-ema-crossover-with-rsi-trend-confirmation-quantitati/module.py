"""EMA 50 / 200 crosses with an RSI 50 filter and a tick bracket, long only in effect, hourly bars: EMA 50 crossing
above EMA 200 with RSI 14 above 50 goes long with a stop and a target twice as far; the bearish cross with RSI below
50 closes the long (the source's short reuses the long's levels and is closed on its own fill).
Port of FMZ strategy #489332 "动态均线交叉结合超买超卖趋势确认量化交易策略-Dynamic-EMA-Crossover-with-RSI-Trend-Confirmation-Quantitative-Trading-Strategy" (Estrategia EMA + RSI).

FMZ source id: 489332

Source
    https://www.fmz.com/strategy/489332 (PineScript v5, FMZ last modified 2025-04-03 15:05:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 250-286), EMA 50 / 200, RSI 14, SL 50 ticks, TP 2 x SL
    long = crossover(ema50, ema200) and rsi > 50;  short = crossunder(ema50, ema200) and rsi < 50   (chart 15 / 60 / 240 / D)
    stop = close - 50 ticks, take = close + 100 ticks; both sides use these same two levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short's exit uses the long's levels (a stop below and a limit above the price), so it fills at once: each
      short opens and closes on its fill. Its only lasting effect is closing a long (the entry reverses it): the
      short signal is ported as a long exit, no short is opened (a zero-length trade).
    * Criterion 2: the 50-tick stop becomes sl_atr x Wilder ATR(14) of the signal bar: 50 ticks of 0.1 on the
      author's hourly BTC_USDT are 5 USD, about 0.0125 hourly ATR (judgement before any backtest; as written the
      stop is hit almost at once); the grid also tries 1 ATR. tp_stop = 2 x the stop; shifted one bar inside stops(),
      re-based on the fill.
    * The timeframe check passes on the source's 1-hour chart. Long only in effect.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
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

NAME = "fmz_489332_ema_50_200_cross_rsi_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.0125, 1.0],
    "tp_ratio": [2.0, 4.0],
}
DEFAULT_PARAMS = {"ema_fast": 50, "ema_slow": 200, "rsi_len": 14, "sl_atr": 0.0125, "tp_ratio": 2.0, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((ef > es) & (ef.shift(1) <= es.shift(1)) & (rsi > 50)).astype(bool)
    long_x = ((ef < es) & (ef.shift(1) >= es.shift(1)) & (rsi < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    d = p["sl_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": d.shift(1), "tp_stop": (p["tp_ratio"] * d).shift(1)}


def portfolio_kwargs(**params):
    return {}
