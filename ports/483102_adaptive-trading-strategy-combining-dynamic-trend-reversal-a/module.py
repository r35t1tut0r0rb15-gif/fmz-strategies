"""0.25 % zigzag reversal line with a stochastic filter and a tick bracket as ATR multiples, daily (broker-day) bars: a
close above the latest zigzag reversal line with the smoothed stochastic %K below 30 goes long; a close below it with
%K above 70 goes short.
Port of FMZ strategy #483102 "动态趋势反转与随机指标结合的自适应交易策略-Adaptive-Trading-Strategy-Combining-Dynamic-Trend-Reversal-and-Stochastic-Indicator" ([RS]ZigZag Percent Reversal with Stochastic Strategy).

FMZ source id: 483102

Source
    https://www.fmz.com/strategy/483102 (PineScript v5, FMZ last modified 2025-02-27 17:00:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 96-230), method MANUAL 0.25 %, stochastic 9 smoothed 3, SL 100 / TP 300 ticks
    zigzag: track the high (low) since the last pivot; reverse when the close passes track -+ pivot[1] x 0.25 %;
    static line = the last non-na reverse line
    buy = close > line and %K < 30; sell = close < line and %K > 70; entry + exit(stop / limit = close -+ ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The zigzag is ported literally (f_zz: both direction blocks run on the same bar; the reverse range uses the
      previous bar's pivot, 0 before the first pivot).
    * Tick distances -> ATR(14) multiples (criterion 2), judged on the author's market (Binance BTC_USDT, mintick 0.01,
      daily ATR about 2,500 USD in early 2025): 100 ticks = 1 USD = 0.0004 ATR, 300 ticks = 0.0012 ATR, as written (the
      bracket is hit within a bar or two). A 1 / 3 ATR reading is the GRID variant. Fractions from the signal bar,
      shifted one bar inside stops() and re-based on the fill (house rule). A same-side signal while held re-places
      the bracket: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00
      America/New_York) stamped with their first minute (as #430984); stops on daily bars: coarse_bar_stop.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, a percentage zigzag, a stochastic and tick distances as ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_483102_zigzag_reversal_line_stoch_tick_bracket"
FAMILY = "zigzag"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_k": [0.0004, 1.0],
    "tp_k": [0.0012, 3.0],
}
DEFAULT_PARAMS = {"percent": 0.25, "k_len": 9, "k_smooth": 3, "atr_len": 14, "sl_k": 0.0004, "tp_k": 0.0012}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _zigzag_line(h, lo, c, pct):
    """f_zz of the source; returns the static reverse line (last non-na reverse line)."""
    m = len(c)
    out = np.full(m, np.nan)
    up = None
    htr = ltr = piv = rline = np.nan
    piv_prev = np.nan
    static = np.nan
    for i in range(m):
        piv_prev_bar = piv_prev
        if i >= 1:
            if up is None:
                up = True
            rr = (0.0 if np.isnan(piv_prev_bar) else piv_prev_bar) * pct
            if up:
                ltr = np.nan
                if np.isnan(htr):
                    htr = h[i] if h[i] > h[i - 1] else h[i - 1]
                elif h[i] > htr:
                    htr = h[i]
                rline = htr - rr
                if c[i] <= rline:
                    piv, up = htr, False
            if not up:
                htr = np.nan
                if np.isnan(ltr):
                    ltr = lo[i] if lo[i] < lo[i - 1] else lo[i - 1]
                elif lo[i] < ltr:
                    ltr = lo[i]
                rline = ltr + rr
                if c[i] >= rline:
                    piv, up = ltr, True
        if not np.isnan(rline):
            static = rline
        out[i] = static
        piv_prev = piv
    return out


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    line = pd.Series(_zigzag_line(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                                  p["percent"] / 100), index=c.index)
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll)).rolling(int(p["k_smooth"])).mean()
    return ((c > line) & (k < 30)).astype(bool), ((c < line) & (k > 70)).astype(bool)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_e, short_e = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": p["sl_k"] * a, "tp_stop": p["tp_k"] * a}


def portfolio_kwargs(**params):
    return {}
