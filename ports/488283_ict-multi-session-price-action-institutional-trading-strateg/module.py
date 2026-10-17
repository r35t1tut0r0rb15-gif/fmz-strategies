"""ICT session sweeps with tick brackets, 1-hour bars: during the New York session (08:20-16:00) a red bar whose high
reaches the London-session high (02:00-08:20, a running maximum over all London bars so far) goes short with a stop
a few ticks over its high and a target a few ticks under its low; between 10:30 and 13:00 a close under the running
London low goes long with a stop under its low and a small target.
Port of FMZ strategy #488283 "多时段价格行为机构交易策略基于ICT理念的日内做空系统-Multi-Session-Price-Action-Institutional-Trading-Strategy-ICT-Based-Intraday-Short-System" (ICT Bread and Butter Sell-Setup).

FMZ source id: 488283

Source
    https://www.fmz.com/strategy/488283 (PineScript v5, FMZ last modified 2025-03-26 15:40:23).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 180-234), sessions London 02:00-08:20, New York 08:20-16:00, Asia 19:00-02:00
    londonHigh / londonLow: var-initialised with the first bar, then max / min of every bar in the London window
    short = high >= londonHigh and in New York and close < open -> entry + exit(stop = high + 10 ticks,
    limit = low - 20 ticks)
    buy = 10:30 <= time <= 13:00 and close < londonLow -> entry + exit(limit = close + 20 ticks, stop = low - 10 ticks)
    asiaSell = time >= 19:00 and time < 02:00 of the same day and close > asiaHigh -> entry short (15 / 10 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): the times are clock times of the bar's open in the chart's time zone: UTC on the
      author's Binance chart (session_tz "UTC", the default) or America/New_York (the CME / New York reading, DST by
      the zone) as the variant. The session levels are never reset, as written (running extremes since the first bar).
    * The Asia window (19:00 to 02:00 of the same date) can never match: asiaSell never fires; not emitted.
    * Criterion 2: on the author's 1-hour ETH_USDT (tick 0.01, 1-hour ATR about 20) a tick is about 0.0005 Wilder
      ATR(14) (judgement before any backtest): 10 / 20 ticks = 10 / 20 x tick_atr x ATR of the signal bar.
    * The bracket is fixed at the signal bar and picked by the signal's side: short sl = (high - close + 10 t) /
      close, tp = (close - low + 20 t) / close; long sl = (close - low + 10 t) / close, tp = 20 t / close; shifted one
      bar inside stops() and re-based on the fill (house rule).
    * A same-side signal while held re-places the bracket from the new bar: mark trailing_stop_pending; the port keeps
      the entry's bracket.
    * Entries reverse (REVERSAL INTENDED); both on one bar: the long, written last, wins. Stop module:
      portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: ADAPT, tick distances -> ATR multiples; session extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: London 02:00, New York 08:20-16:00, buy window 10:30-13:00 in session_tz (UTC as written; America/New_York, DST by the zone, as the variant).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488283_ict_london_sweep_tick_bracket"
FAMILY = "session_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "America/New_York"],
    "tick_atr": [0.0005, 0.005],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "tick_atr": 0.0005, "sl_ticks": 10, "tp_ticks": 20, "atr_len": 14}


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
    loc = bars_df.index.tz_convert(p["session_tz"])
    mins = (loc.hour * 60 + loc.minute).to_numpy()
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    if m == 0:
        return le, se
    lon_h, lon_l = h[0], lo[0]                     # var-initialised with the first bar
    for i in range(m):
        if 2 * 60 <= mins[i] < 8 * 60 + 20:
            lon_h, lon_l = max(lon_h, h[i]), min(lon_l, lo[i])
        in_ny = 8 * 60 + 20 <= mins[i] < 16 * 60
        short_e = h[i] >= lon_h and in_ny and c[i] < o[i]
        long_e = 10 * 60 + 30 <= mins[i] <= 13 * 60 and c[i] < lon_l
        le[i] = long_e
        se[i] = short_e and not long_e             # both on one bar: the long, written last, wins
    return le, se


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    tick = p["tick_atr"] * _atr(bars_df, int(p["atr_len"]))
    sl_t, tp_t = p["sl_ticks"] * tick, p["tp_ticks"] * tick
    long_e, short_e = pd.Series(le, index=c.index), pd.Series(se, index=c.index)
    sl = ((c - lo + sl_t) / c).where(long_e, ((h - c + sl_t) / c).where(short_e)).shift(1)
    tp = (tp_t / c).where(long_e, ((c - lo + tp_t) / c).where(short_e)).shift(1)
    return {"sl_stop": sl, "tp_stop": tp}


def portfolio_kwargs(**params):
    return {}
