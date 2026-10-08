"""TD count + MACD + RSI + Bollinger: from flat, go long on the second close in a row above the
close 4 bars earlier when the MACD histogram has been negative for 5 bars, RSI(14) <= 43 and
the close is not above the upper band (shorts mirrored); each trade exits at a profit target.
Port of FMZ strategy #426477 "Multi Indicator Convergence Trading Strategy".

Source
    https://www.fmz.com/strategy/426477 (PineScript v2, FMZ last modified 2023-09-12 14:27:41).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 90-145), RSI difference -7, profit 50, stop off
    TD = close > close[4] ? nz(TD[1]) + 1 : 0;  TS mirrors
    Buy  = TD == 2 and hist < 0 on bars 0..4 and rsi(14) <= 50 - 7 and not close > upper BB(20, 2)
    Sell = TS == 2 and hist > 0 on bars 0..4 and rsi(14) >= 50 + 7 and not close < lower BB
    position == 0 -> entry;  exit(profit = 50 * 10 ticks, loss = 1e6 ticks: stop off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 500-tick target is instrument-specific (BTC: 50 USDT, a small fraction of
      a daily ATR). It becomes tp_atr x ATR(14) at the signal bar, a tp_stop fraction shifted one
      bar. The stop is off by default (useStopLoss false): no sl_stop.
    * Entries need a flat position, so simulate() mirrors the engine's target from the fill bar
      on. Opposite entries cannot occur while a position is open (upon_opposite_entry "ignore").
    * stdev is Pine's population deviation. TDUp / TDDn only plot.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.
      Target on daily bars: coarse_bar_stop.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_426477_td_macd_rsi_bb"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "rsi_diff": [-7, -14],
    "tp_atr": [0.25, 1.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_diff": -7, "tp_atr": 0.25}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi_pine(close, n):
    """rsi() as Pine defines it: 100 when the average loss is 0, 0 when the average gain is 0."""
    d = close.diff()
    up, down = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    rsi = 100.0 - 100.0 / (1.0 + up / down)
    return rsi.mask(up == 0, 0.0).mask(down == 0, 100.0).where(up.notna() & down.notna())


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _count(cond):
    out = np.zeros(len(cond))
    run = 0
    for i in range(len(cond)):
        run = run + 1 if cond[i] else 0
        out[i] = run
    return out


def _conditions(bars, p):
    c = bars["close"]
    td = _count((c > c.shift(4)).to_numpy())
    ts = _count((c < c.shift(4)).to_numpy())
    ema = lambda x, n: x.ewm(span=n, adjust=False).mean()
    macd = ema(c, 12) - ema(c, 26)
    hist = macd - ema(macd, 9)
    neg = (hist < 0).rolling(5).sum() == 5
    pos = (hist > 0).rolling(5).sum() == 5
    rsi = _rsi_pine(c, 14)
    basis = c.rolling(20).mean()
    dev = 2 * c.rolling(20).std(ddof=0)
    buy = (td == 2) & neg & (rsi <= 50 + p["rsi_diff"]) & ~(c > basis + dev)
    sell = (ts == 2) & pos & (rsi >= 50 - p["rsi_diff"]) & ~(c < basis - dev)
    return buy.to_numpy(), sell.to_numpy()


def _tp_frac(bars, p):
    return p["tp_atr"] * _atr_pine(bars, ATR_LEN) / bars["close"]


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _conditions(bars_df, p)
    tpf = _tp_frac(bars_df, p).to_numpy()
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pending, frac, target = 0, 0, np.nan, np.nan
    for i in range(m):
        if pending:
            pos = pending
            target = o[i] * (1 + pos * frac)
            pending = 0
        if pos == 1 and h[i] >= target:
            pos = 0
        elif pos == -1 and lo[i] <= target:
            pos = 0
        if pos == 0 and not pending:
            if buy[i]:
                le[i], pending, frac = True, 1, tpf[i]
            elif sell[i]:
                se[i], pending, frac = True, -1, tpf[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = simulate(bars_df, **params)
    return {"tp_stop": _tp_frac(bars_df, p).where(le | se).shift(1)}


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
