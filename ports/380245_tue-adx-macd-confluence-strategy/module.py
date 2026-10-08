"""TUE ADX / MACD confluence strategy (Zer3192): entering the DI+ / MACD long state during New York
09:30-16:00 weekday bars goes long (short mirrors); a long closes when the long state ends, a short
when the short state ends; each position carries a fixed stop below / above its entry.
Port of FMZ strategy #380245 "TUE ADX/MACD Confluence Strategy V1.0".

Source
    https://www.fmz.com/strategy/380245 (PineScript v5, author Zer3192, FMZ last modified
    2022-08-27 16:37:33). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 52-136), DMI 14 / 10, MACD 12 / 26 / 9, session
"0930-1600:23456" New York, stop 1.0 (price units)
    longcheck = DI+ > DI- and macd > signal;  shortcheck mirrors
    trade = longcheck ? 1 : shortcheck ? -1 : trade[1]   (re-declared 0 each bar, as #368715)
    entry long when trade turns 1 inside the session; exit(stop = avg price - 1.0)
    close long when longcheck[1] and not longcheck   (shorts mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session filter is logic (kept): a bar opening Monday-Friday 09:30-16:00 New York time
      may open trades; closes may happen any time.
    * Criterion 2: the 1.0 stop is in price units (cents / ticks per the tooltip). It becomes
      stop_atr x ATR(14) at the signal bar, an sl_stop fraction shifted one bar inside stops().
      Note: on BTC 1.0 is about 0 ATR, i.e. the source stop would trigger almost at once.
    * "long state ends" is a close-based exit signal. Stops on 4-hour bars: coarse_bar_stop.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}).
    * FREQ = "4h" from the backtest header.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_380245_dmi_macd_session_stop"
FAMILY = "directional_movement"  # proposed 2026-10-07, user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
ATR_LEN = 14  # criterion 2 conversion length (fixed)

GRID = {
    "di_len": [10, 14],
    "stop_atr": [0.5, 1.0, 2.0],
}
DEFAULT_PARAMS = {"di_len": 14, "adx_smooth": 10, "macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                  "stop_atr": 1.0, "session_start": 570, "session_end": 960}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _signals(bars_df, p):
    plus, minus, _ = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_smooth"]))
    c = bars_df["close"]
    macd = c.ewm(span=int(p["macd_fast"]), adjust=False).mean() - c.ewm(span=int(p["macd_slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["macd_signal"]), adjust=False).mean()
    lc = ((plus > minus) & (macd > sig)).to_numpy()
    sc = ((minus > plus) & (sig > macd)).to_numpy()
    m = len(c)
    trade = np.zeros(m)
    for i in range(m):
        trade[i] = 1.0 if lc[i] else (-1.0 if sc[i] else (trade[i - 1] if i else 0.0))
    prev = np.concatenate([[np.nan], trade[:-1]])
    ny = bars_df.index.tz_convert("America/New_York")
    minutes = np.asarray(ny.hour * 60 + ny.minute)
    in_session = (np.asarray(ny.weekday) < 5) & (minutes >= p["session_start"]) & (minutes < p["session_end"])
    le = (trade == 1) & (prev != 1) & in_session
    se = (trade == -1) & (prev != -1) & in_session
    lag = lambda a: np.concatenate([[False], a[:-1]])
    lx = lag(lc) & ~lc & ~le & ~se
    sx = lag(sc) & ~sc & ~le & ~se
    return le, lx, se, sx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in _signals(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _ = _signals(bars_df, p)
    frac = p["stop_atr"] * _atr_pine(bars_df, ATR_LEN) / bars_df["close"]
    return {"sl_stop": frac.where(le | se).shift(1)}


def portfolio_kwargs(**params):
    return {}
