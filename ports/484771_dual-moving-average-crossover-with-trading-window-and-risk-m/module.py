"""SMA 10 / 25 crosses inside a trading window with a tick bracket and a 15:00 close-all, 1-minute bars: in the window
(minutes 30-59 of hours 08-14, as written) the fast SMA crossing above the slow one goes long with a stop and a target
50 ticks from the signal close; the cross down goes short, but the short's levels sit on the wrong side, so a short
is closed at the open after its fill bar; every position is closed at 15:00.
Port of FMZ strategy #484771 "双均线交叉带定时交易窗口与止盈止损策略-Dual-Moving-Average-Crossover-with-Trading-Window-and-Risk-Management-Strategy" (Custom MACrossOver).

FMZ source id: 484771

Source
    https://www.fmz.com/strategy/484771 (PineScript v5, FMZ last modified 2025-03-04 10:59:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 257-298), SMA 10 / 25, stop 50 ticks, target 50 ticks, quantity 2
    market_open = hour >= 8 and minute >= 30 and hour < 15
    in the window: crossover -> entry long, tradeEntryPrice = close; else crossunder -> entry short, tradeEntryPrice
    every bar in a position: exit(stop = tradeEntryPrice - 50 ticks, limit = tradeEntryPrice + 50 ticks) for long AND
    short;  hour == 15 and minute == 0 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): hour / minute of the bar's open in the chart's time zone, as written (only minutes
      30-59 of each hour 08-14 qualify): UTC on the author's Binance chart (session_tz "UTC", the default) or
      America/Chicago (the evident CME hours, DST by the zone) as the variant; the 15:00 close-all in the same zone.
    * Criterion 2: on the author's 1-minute SOL_USDT (tick 0.01, 1-minute ATR about 0.3) 50 ticks are about 1.7 Wilder
      ATR(14) (judgement before any backtest). Longs: sl_stop = tp_stop = k_atr x ATR / close of the signal bar,
      shifted one bar inside stops() and re-based on the fill; later in-window signals move tradeEntryPrice and the
      re-issued exit: mark trailing_stop_pending.
    * Shorts get the same levels (a buy stop below and a buy limit above the entry): both trigger at once, so the short
      closes at the open after its fill bar: an exit signal on the fill bar, no stops for shorts (NaN).
    * Entries reverse (REVERSAL INTENDED). simulate() mirrors the long bracket from the fill bar (#430254). Stop
      module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket from the signal bar (moves marked).
    2 generic: ADAPT, tick distances -> ATR multiples; moving averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the quantity 2 quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: window minutes 30-59 of hours 08-14 and a 15:00 close-all in session_tz (UTC as written; America/Chicago, DST by the zone, as the variant).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_484771_sma_cross_window_tick_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "America/Chicago"],
    "k_atr": [1.7, 3.0],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "fast": 10, "slow": 25, "k_atr": 1.7, "atr_len": 14}


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


def _signals(bars_df, p):
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    loc = bars_df.index.tz_convert(p["session_tz"])
    hr, mn = loc.hour.to_numpy(), loc.minute.to_numpy()
    window = (hr >= 8) & (mn >= 30) & (hr < 15)
    go_l = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy() & window
    go_s = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy() & window & ~go_l
    eod = (hr == 15) & (mn == 0)
    return go_l, go_s, eod


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    go_l, go_s, eod = _signals(bars_df, p)
    k = (p["k_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).to_numpy(dtype=float)
    ov, hv, lv = (bars_df[x].to_numpy(dtype=float) for x in ("open", "high", "low"))
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, fill_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos == 1 and i >= fill_i:                     # mirror of the long bracket from the fill price
            e = ov[fill_i]
            if lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + s_):
                pos = 0
        start = pos
        if go_l[i] and pos != 1:
            pos, fill_i, s_ = 1, i + 1, k[i]
        elif go_s[i] and pos != -1:
            pos, fill_i = -1, i + 1
        if start == -1 and pos == -1 and i == fill_i:    # the short's wrong-side exit fills at the next open
            pos = 0
        if eod[i] and start != 0 and pos == start:
            pos = 0
        if pos != start:
            le[i] = pos == 1
            se[i] = pos == -1
            lx[i] = start == 1 and pos == 0
            sx[i] = start == -1 and pos == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    go_l, _, _ = _signals(bars_df, p)
    k = (p["k_atr"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).where(pd.Series(go_l, index=bars_df.index))
    return {"sl_stop": k.shift(1), "tp_stop": k.shift(1)}


def portfolio_kwargs(**params):
    return {}
