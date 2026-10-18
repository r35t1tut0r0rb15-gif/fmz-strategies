"""Counter-trend fades outside two bands in a quiet market, 5-minute bars: a close over both the Bollinger upper band (20, 2 sd) and the 1 % envelope top, with the ADX
under 30 and the slow stochastic over 50, goes short; the mirror goes long; the exit rules are as written (loose, they close at once).
Port of FMZ strategy #435980 "Hedging Oscillation Reversal Strategy" (Contrarian Scalping Counter Trend).

FMZ source id: 435980

Source
    https://www.fmz.com/strategy/435980 (PineScript v5, FMZ last modified 2023-12-20 15:43:18).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 184-241), Bollinger 20 / 2 sd; envelope 20 / 1 %; ADX 14 / 14 under 30; stochastic 50 / 20 around 50
    short = close > upper and close > upper_env and adx < 30 and stoch > 50;  long = close < lower and close < lower_env and adx < 30 and stoch < 50
    short_exit = close < lower or close < lower_env or stoch < 50;  long_exit = close > lower or close > lower_env or stoch > 50   (as written)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit tests as written are loose: long_exit is true whenever the close is over the lower band
      (nearly always), so a long is closed on the bar after it opens; the short exit needs the close under the
      lower envelope or the stochastic under 50. The four orders of one bar are filled in the script's call
      order at the next open (entry short, close short, entry long, close long). The ADX is the built-in
      style DMI with RMA smoothing and fixnan. REVERSAL INTENDED. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands, envelope, ADX and stochastic.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435980_band_envelope_counter_trend"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "percent": [1.0, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "percent": 1.0, "adxlen": 14, "dilen": 14, "periodk": 50, "smoothk": 20}


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


def _fixnan(s):
    v = s.to_numpy(dtype=float).copy()
    for i in range(1, len(v)):
        if np.isnan(v[i]):
            v[i] = v[i - 1]
    return pd.Series(v, index=s.index)


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    plus_dm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    minus_dm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(up.notna())
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    a = 1 / di_len
    trn = tr.ewm(alpha=a, adjust=False).mean()
    plus = _fixnan(100 * plus_dm.ewm(alpha=a, adjust=False).mean() / trn)
    minus = _fixnan(100 * minus_dm.ewm(alpha=a, adjust=False).mean() / trn)
    s = plus + minus
    return 100 * (((plus - minus).abs() / s.where(s != 0, 1.0)).ewm(alpha=1 / adx_len, adjust=False).mean())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    k = float(p["percent"]) / 100.0
    upper_env, lower_env = basis * (1 + k), basis * (1 - k)
    sig = _adx(h, lo, c, int(p["dilen"]), int(p["adxlen"]))
    pk = int(p["periodk"])
    with np.errstate(invalid="ignore", divide="ignore"):
        raw = 100 * (c - lo.rolling(pk).min()) / (h.rolling(pk).max() - lo.rolling(pk).min())
    stock = raw.rolling(int(p["smoothk"])).mean()
    short = ((c > upper) & (c > upper_env) & (sig < 30) & (stock > 50)).fillna(False).to_numpy()
    long_ = ((c < lower) & (c < lower_env) & (sig < 30) & (stock < 50)).fillna(False).to_numpy()
    short_exit = ((c < lower) | (c < lower_env) | (stock < 50)).fillna(False).to_numpy()
    long_exit = ((c > lower) | (c > lower_env) | (stock > 50)).fillna(False).to_numpy()
    m = len(short)
    held = np.zeros(m, dtype=np.int8)
    pos = 0
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:          # fills at this bar's open, in the script's call order
            a, b, cc, d = pend
            if a and pos >= 0:
                pos = -1
            if b and pos == -1:
                pos = 0
            if cc and pos <= 0:
                pos = 1
            if d and pos == 1:
                pos = 0
        held[i] = pos
        pend = (bool(short[i]), bool(short_exit[i]), bool(long_[i]), bool(long_exit[i]))
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
