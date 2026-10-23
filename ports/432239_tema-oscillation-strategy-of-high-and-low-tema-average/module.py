"""Short only, broker days: a volume-weighted MACD (VWMA-style EMA 13 against EMA 21, signal 5) histogram under 0 with the close under the Hull MA 400 and the TEMA 5 of hlc3 under the TEMA 8 goes short; the histogram over 0, the close over the Hull MA or the TEMA difference crossing above 0 closes; a 1 % target and a 4 % stop of the close.
Port of FMZ strategy #432239 "高低TEMA平均值震荡策略Oscillation-Strategy-of-High-and-Low-TEMA-Average" (TEMA_HMA_VWMACD short strategy).

FMZ source id: 432239

Source
    https://www.fmz.com/strategy/432239 (PineScript v4, FMZ last modified 2023-11-15 17:49:52).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 131-185), VWMACD 13 / 21, signal 5; HMA 400; TEMA 5 / 8 of hlc3; TP 1 %, SL 4 % (of the close, in ticks); start 2017-12-17
    Macd = ema(v x c, 13) / ema(v, 13) - ema(v x c, 21) / ema(v, 21);  Hist = Macd - ema(Macd, 5);  tm = tema(hlc3, 5) - tema(hlc3, 8)
    Hist < 0 and hullma > close and tema1 < tema2 -> entry BUY (short);  Hist > 0 or hullma < close or crossover(tm, 0) -> close BUY;  exit(profit = close x 1 % / mintick, loss = close x 4 % / mintick) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry id "BUY" opens a SHORT, as written; there is no long side. The exit distances are 1 % and
      4 % of the LATEST close, re-sent every bar; the port fixes them at the signal close as fractions of
      the fill (mark trailing_stop_pending), as #426389. The entry and close conditions cannot hold on the
      same bar. pyramiding is the default 1. The Hull MA uses length / 2 = 200 and floor(sqrt(400)) = 20.
      The author's start date (2017-12-17) is dropped. 100 % of equity and the commission are sizing and
      costs. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at the signal close as fractions of the fill.
    2 generic: PASS, volume-weighted MACD and TEMA trend shorts under a Hull MA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, commission 0.018 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume-weighted MACD (ema(volume x close) / ema(volume), 13 and 21); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the author's 2017-12-17 start dropped).
Short only. Opposite entries cannot occur.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_432239_vwmacd_hma400_tema_short_pct_bracket"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hma_len": [400, 200],
    "tema_slow": [8, 13],
}
DEFAULT_PARAMS = {"vw_slow": 13, "vw_fast": 21, "signal": 5, "hma_len": 400, "tema_fast": 5, "tema_slow": 8,
                  "tp": 0.01, "sl": 0.04}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _tema(x, n):
    e1 = _ema(x, n)
    e2 = _ema(e1, n)
    e3 = _ema(e2, n)
    return 3 * e1 - 3 * e2 + e3


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))

    def vw(n):
        ev = _ema(v, n)
        return _ema(v * c, n) / ev.where(ev != 0)

    macd = vw(int(p["vw_slow"])) - vw(int(p["vw_fast"]))
    hist = macd - _ema(macd, int(p["signal"]))
    n = int(p["hma_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(np.floor(np.sqrt(n))))
    src = (h + lo + c) / 3
    t1, t2 = _tema(src, int(p["tema_fast"])), _tema(src, int(p["tema_slow"]))
    tm = t1 - t2
    up = (tm > 0) & (tm.shift(1) <= 0)
    ent = ((hist < 0) & (hull > c) & (t1 < t2)).to_numpy()
    ext = ((hist > 0) | (hull < c) | up).to_numpy()
    m = len(ent)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            se[i], pos = True, -1
        elif pos == -1 and ext[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return false, false.copy(), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    sl_f, tp_f = float(p["sl"]) * k, float(p["tp"]) * k
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
