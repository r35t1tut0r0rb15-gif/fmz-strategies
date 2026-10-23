"""Broker days: the EMA 8 crossing over the EMA 21 above the SMA 100 and 200 with MACD over its signal and RSI over 50 goes long; the mirror goes short; a 5 % close target (5 % ABOVE the entry for shorts too, as written) is only checked after a repeated signal re-arms the script's flag; reversing.
Port of FMZ strategy #475602 "多指标趋势跟踪期权交易EMA交叉策略-Multi-Indicator-Trend-Following-Options-Trading-EMA-Cross-Strategy" (OptionsMillionaire Strategy with Take Profit Only).

FMZ source id: 475602

Source
    https://www.fmz.com/strategy/475602 (PineScript v5, FMZ last modified 2024-12-20 14:49:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 89-174), EMA 8 / 21; SMA 100 / 200; MACD 12 / 26 / 9; RSI 14; TP 5 % from the signal close; qty 1
    callSignal and not positionOpen -> entry Call, entryPrice := close, positionOpen := true;  putSignal and not positionOpen -> entry Put (same)
    if positionOpen: level = entryPrice x 1.05;  long and close >= level -> exit(limit = level);  short and close <= level -> exit(limit = level)
    if position_size == 0: positionOpen := false

Interpretation choices (Pine rules in SURVEY_README.md)
    * positionOpen is reset on every bar the strategy is flat at the close, which includes the signal
      bar (the fill comes at the next open), so during a trade it is false and the target test does not
      run; it runs only after a later signal of the same side while in the trade (that entry adds
      nothing but re-arms the flag and the entry price). Then a long exits once a close reaches 5 % above
      that price, and a short (whose level is also 5 % ABOVE) exits on that same bar's test. The limit
      exit is followed in the signals as a close at the next open. The opposite signal reverses (the flag
      does not block it). VWAP only plots. REVERSAL INTENDED. qty 1 is sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked target followed in the signals.
    2 generic: PASS, EMA 8 / 21 crossings in the SMA 100 / 200 trend with MACD and RSI.
    3 crypto-exchange-only: no (exchange pair in the header only (options named in the title)).
    4 signals only: qty 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_475602_ema8_21_cross_sma_trend_macd_rsi_flag_target_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tp": [0.05, 0.1],
    "fast": [8, 12],
}
DEFAULT_PARAMS = {"tp": 0.05, "fast": 8}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=21, adjust=False).mean()
    s100, s200 = c.rolling(100).mean(), c.rolling(200).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    call = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > s100) & (c > s200) & (macd > sig) & (r > 50)).to_numpy()
    put = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < s100) & (c < s200) & (macd < sig) & (r < 50)).to_numpy()
    cn = c.to_numpy(dtype=float)
    k = 1 + float(p["tp"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, flag, ep = 0, False, np.nan
    for i in range(m):
        new = pos
        if call[i] and not flag:
            new, flag, ep = (1 if pos != 1 else pos), True, cn[i]
        if put[i] and not flag:
            new, flag, ep = (-1 if pos != -1 else pos), True, cn[i]
        if flag and new == pos:
            if pos == 1 and cn[i] >= ep * k:
                new = 0
            elif pos == -1 and cn[i] <= ep * k:          # the short's level is also above the entry
                new = 0
        if pos == 0:
            flag = False                  # position_size == 0 at this close
        if new != pos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
