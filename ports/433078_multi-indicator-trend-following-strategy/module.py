"""Five-minute bars: a close above the SSL-hybrid Keltner band (EMA 30 + 0.2 x EMA 30 of the true range) that was not above it 4 bars back, a MACD at or above its Bollinger upper line (SMA 10 + 1 sd) and positive after a positive MACD under the line one bar back, and buyers' volume share since the 09:15 UTC bar over 50 % go long; the mirror set goes short; a 1 % target from the fill and a 2 % close-based stop; reversing.
Port of FMZ strategy #433078 "Multi indicator Trend Following Strategy" (Strategy Myth-Busting #7 - MACDBB+SSL+VSF - [MYN]).

FMZ source id: 433078

Source
    https://www.fmz.com/strategy/433078 (PineScript v5, FMZ last modified 2023-11-24 11:10:27).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 234-850), SSL1 / baseline EMA 30, channel 0.2 x EMA(tr, 30); MACD 12 / 26, BB 10 x 1; pullback look-back 4, MACD look-back 1; VSF from the 0915-0916 bar (Mon-Fri); TP1 1 % (100 %); SL 2 % (close); ADX off
    longCondition = (src > BBMC and color_bar blue) and (blue and (f_priorBarsSatisfied(red, 4) or f_priorBarsSatisfied(gray, 4))) and round(Pos) > 50 and (mc lime and macd > 0 and f_priorBarsSatisfied(macd > 0 and mc red, 1))
    entry Long (not in a long) / Short (not in a short);  exit TP1 profit = per(1) (qty 100 %);  close when close < avg x 0.98 (long) / > avg x 1.02 (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_priorBarsSatisfied declares a NEW local "returnVal = true" inside its loop (= not :=), so the
      outer flag never changes and the function returns the value of its loop's last iteration: the
      condition exactly N bars back (4 for the pullback, 1 for the MACD), not "any of the last N" as the
      comments intend (weird case); ported as the code returns it. The VSF buyer / seller volume shares sum
      the bars from the latest 09:15 bar (session '0915-0916:23456', Mon-Fri) to the previous bar; on the
      09:15 bar itself the loop "for i = 1 to 0" runs downward over that bar and the one before, as Pine
      does. The session clock is read as UTC (no backtest header; the alert prefix names a crypto venue);
      a zero-range bar makes the day's shares na until the next 09:15 bar, as written. TP1 is a full exit
      1 % from the average price (TP2-4 at 100 % never come first); the script sends it from the bar after
      the fill, the port from the fill; the 2 % stop is a strategy.close on a bar close, ported in the
      signals with the average price = the fill. The SSL2 / exit lines, ATR bands and the ADX (off) feed no
      order. REVERSAL INTENDED. The equity-based contracts and leverage 1 are sizing. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "5min": no backtest header; the source's comment "//5 min"
      names it (as the titled-bar-size ports).

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent target from the fill, close-based stop in the signals.
    2 generic: PASS, SSL-hybrid trend, MACD Bollinger continuation and session volume strength.
    3 crypto-exchange-only: no (no backtest header; bar size from the source's comment).
    4 signals only: qty = equity x leverage / close (leverage 1), 1 % of equity default, commission 0.075 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Volume Strength Finder buyer / seller volume shares since the 09:15 bar; exchange volume to be compared later (Austin, 2026-10-23).
Session open: VSF anchored at the 09:15 UTC bar, Mon-Fri (session '0915-0916:23456' read in UTC).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433078_ssl_hybrid_macd_bb_session_volume_strength_5m_reversal"
FAMILY = "ssl_hybrid"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "5min"  # no backtest header: the source's comment "//5 min"
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.01, 0.02],
    "sl": [0.02, 0.03],
}
DEFAULT_PARAMS = {"tp": 0.01, "sl": 0.02, "base_len": 30, "multy": 0.2, "bb_len": 10, "bb_dev": 1.0,
                  "pullback_back": 4, "macd_back": 1}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["base_len"])
    bbmc = _ema(c, n)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    rng = _ema(tr, n)
    upk, lok = bbmc + rng * float(p["multy"]), bbmc - rng * float(p["multy"])
    cb = pd.Series(np.where(c > upk, 1, np.where(c < lok, -1, 0)), index=c.index)
    kb = int(p["pullback_back"])
    cbk = cb.shift(kb)
    ssl_l = (c > bbmc) & (cb == 1) & cbk.notna() & (cbk != 1)
    ssl_s = (c < bbmc) & (cb == -1) & cbk.notna() & (cbk != -1)
    macd = _ema(c, 12) - _ema(c, 26)
    nb = int(p["bb_len"])
    upper = macd.rolling(nb).std(ddof=0) * float(p["bb_dev"]) + macd.rolling(nb).mean()
    lime = macd >= upper
    km = int(p["macd_back"])
    m_l = lime & (macd > 0) & ((macd > 0) & ~lime).shift(km, fill_value=False)
    m_s = ~lime & (macd < 0) & ((macd < 0) & lime).shift(km, fill_value=False)
    # Volume Strength Finder from the latest 09:15 bar (Mon-Fri, UTC)
    rngb = (h - lo).to_numpy(dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        pv = v.to_numpy(dtype=float) * (c - lo).to_numpy(dtype=float) / rngb
        nv = v.to_numpy(dtype=float) * (h - c).to_numpy(dtype=float) / rngb
    pv = np.where(rngb == 0, np.nan, pv)
    nv = np.where(rngb == 0, np.nan, nv)
    ix = c.index
    t1 = np.asarray((ix.hour == 9) & (ix.minute == 15) & (ix.dayofweek < 5))
    m = len(c)
    sp, sn = np.zeros(m), np.zeros(m)
    run_p = run_n = None
    for i in range(m):
        if t1[i]:
            sp[i] = (pv[i - 1] if i else np.nan) + pv[i]
            sn[i] = (nv[i - 1] if i else np.nan) + nv[i]
            run_p, run_n = pv[i], nv[i]
        elif run_p is not None:
            sp[i], sn[i] = run_p, run_n
            run_p, run_n = run_p + pv[i], run_n + nv[i]
    with np.errstate(invalid="ignore", divide="ignore"):
        tot = sp + sn
        pos_s, neg_s = sp / tot * 100, sn / tot * 100
    vsf_l = np.floor(pos_s + 0.5) > 50
    vsf_s = np.floor(neg_s + 0.5) > 50
    long_c = (ssl_l & m_l).to_numpy() & vsf_l
    short_c = (ssl_s & m_s).to_numpy() & vsf_s
    return long_c, short_c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c = _signals(bars_df, p)
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, avg, need_fill = 0, np.nan, False
    for i in range(m):
        fresh = False
        if need_fill:
            avg, need_fill, fresh = ov[i], False, True        # the entry fills at this bar's open
        if not fresh:                                          # the target, sent from the bar after the fill
            if pos == 1 and hv[i] >= avg * (1 + tp):
                pos = 0
            elif pos == -1 and lv[i] <= avg * (1 - tp):
                pos = 0
        tgt = 1 if long_c[i] else (-1 if short_c[i] else 0)
        if tgt != 0 and tgt != pos and i + 1 < m:
            if tgt == 1:
                le[i] = True
            else:
                se[i] = True
            pos, need_fill = tgt, True
        elif pos == 1 and cv[i] < avg * (1 - sl):
            lx[i], pos = True, 0
        elif pos == -1 and cv[i] > avg * (1 + sl):
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
