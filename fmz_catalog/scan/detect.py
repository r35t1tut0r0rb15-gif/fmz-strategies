"""Tag every FMZ strategy with the indicators it uses.

Usage (from the repo root):
    python fmz_catalog/scan/extract_sources.py /tmp/code.json
    python fmz_catalog/scan/detect.py /tmp/code.json fmz_catalog/scan/usage.json

A strategy counts as using an indicator when its source code matches one of
the indicator's patterns: a built-in call (Pine ``ta.x(`` or v1-v4 bare
``x(``, FMZ ``TA.X(``, ``talib.X(``, MyLanguage ``X(``), a custom function
name, or a formula fingerprint. Strategy titles are tagged separately
(``title_only``) to catch indicators the patterns miss.
"""

import json
import re
import sys


def B(*names):
    """Pine built-in call, v5 ``ta.name(`` or v1-v4 bare ``name(``."""
    alt = "|".join(names)
    return rf"(?:\bta\.(?:{alt})\s*\(|(?<![\w\.])(?:{alt})\s*\()"


def V(*names):
    """Pine built-in variable such as ``ta.obv`` / v4 ``obv``."""
    alt = "|".join(names)
    return rf"(?:\bta\.(?:{alt})\b|(?<![\w\.])(?:{alt})\b(?!\s*[\(=]))"


def F(*names):
    """User function definition ``name(...) =>``."""
    alt = "|".join(names)
    return rf"^\s*(?:{alt})\s*\([^)\n]*\)\s*=>"


FMZ = lambda *n: rf"\bTA\.(?:{'|'.join(n)})\s*\("          # noqa: E731
TL = lambda *n: rf"\btalib\.(?:{'|'.join(n)})\s*\("        # noqa: E731

# key: (label, existing tv_indicators function or None, [code patterns], title pattern)
D = {
    # --- moving averages -------------------------------------------------
    "sma": ("SMA", "sma", [B("sma"), FMZ("MA", "SMA"), TL("SMA", "MA")], r"\bsma\b|simple moving"),
    "ema": ("EMA", "ema", [B("ema"), FMZ("EMA"), TL("EMA")], r"\bema\b|exponential moving"),
    "rma": ("RMA / SMMA (Wilder)", "rma", [B("rma"), F("smma", "calc_smma", "pine_rma"), r"\bsmma\b"], r"\bsmma\b|\brma\b|smoothed moving"),
    "wma": ("WMA", "wma", [B("wma"), TL("WMA")], r"\bwma\b|weighted moving"),
    "vwma": ("VWMA", "vwma", [B("vwma")], r"\bvwma\b"),
    "hma": ("Hull MA", "hma", [B("hma"), F("hma", "hullma", "f_hma", "gethullma"), r"wma\(\s*2\s*\*\s*(?:ta\.)?wma"], r"\bhull\b|\bhma\b"),
    "ehma_thma": ("EHMA / THMA (Hull Suite)", "ehma / thma", [F("ehma", "thma", "hma3")], r"hull suite"),
    "dema": ("DEMA", "dema", [F("dema", "f_dema", "variant_doubleema"), r"2\s*\*\s*(\w+)\s*-\s*(?:ta\.)?ema\(\s*\1"], r"\bdema\b"),
    "tema": ("TEMA", "tema", [F("tema", "variant_tripleema"), r"3\s*\*\s*\(?\s*\w+\s*-\s*\w+\s*\)?\s*\+\s*\w*ema"], r"\btema\b|triple ema|triple exponential"),
    "alma": ("ALMA", "alma", [B("alma")], r"\balma\b|arnaud"),
    "lsma": ("LSMA / linreg", "lsma / linreg", [B("linreg"), TL("LINEARREG")], r"\blsma\b|least squares|linear regression"),
    "swma": ("SWMA", "swma", [B("swma")], None),
    "zlema": ("ZLEMA (zero lag EMA)", "zlema", [F("zlema", "zlema_func", "calc_zlema", "f_zlema", "f_lb_zlema", "variant_zerolagema"), r"zxLag", r"\bzlema\b"], r"zlema|zero.?lag"),
    "t3": ("T3 (Tillson)", "t3", [F("t3", "gett3", "gd"), r"\bt3\b", r"xe6"], r"\bt3\b|tillson"),
    "kama": ("KAMA", "kama", [F("kama", "getkama", "ama"), r"\bkama\b", TL("KAMA")], r"\bkama\b|kaufman"),
    "vidya": ("VIDYA / VAR", "vidya", [F("var_func", "var_func1", "var_func2", "vidya"), r"vCMO", r"\bvidya\b"], r"vidya|variable index"),
    "wwma": ("WWMA (Welles Wilder MA, zero-seeded)", "extra.wwma", [F("wwma_func", "wwma_func1", "wwma_func2"), r"\bwwma\b"], None),
    "tsf": ("TSF (time series forecast)", "extra.tsf", [F("tsf_func", "tsf_func1", "tsf_func2"), r"\btsf\b", TL("TSF")], r"time series forecast"),
    "trima": ("TMA / TRIMA", "trima", [r"sma\(\s*(?:ta\.)?sma\([^)]*ceil", F("trima", "variant_trima"), TL("TRIMA")], r"\btrima\b|triangular"),
    "mcginley": ("McGinley Dynamic", "mcginley", [F("mcg", "mcginley"), r"mcginley"], r"mcginley"),
    "jma": ("Jurik MA (JMA)", "extra.jma", [F("jma", "f_jma", "get_jurik"), r"\bjma\b|jurik"], r"jurik|\bjma\b"),
    "frama": ("FRAMA", "frama", [r"frama"], r"frama|fractal adaptive"),
    "supersmoother": ("Ehlers Super Smoother (2-pole)", "supersmoother", [F("variant_supersmoother", "get2polessf", "supersmoother", "f_pole"), r"supersmoother|super_smoother|1\.414\s*\*"], r"super ?smoother"),
    "ssf3": ("Ehlers 3-pole Super Smoother", "extra.ssf3", [F("get3polessf")], None),
    "gaussian": ("Ehlers Gaussian filter", "extra.gaussian_filter / gaussian_channel", [F("variant_gauss", "gauss", "f_filt9x", "getpoles"), r"gaussian"], r"gaussian"),
    "laguerre": ("Laguerre filter / Laguerre RSI", "laguerre / laguerre_rsi", [r"laguerre", r"\bL0\s*:?=\s*\(1\s*-\s*gamma"], r"laguerre"),
    "kalman": ("Kalman filter", "extra_ma.kalman_alpha_beta", [r"kalman|kahlman"], r"kalman"),
    "kernel": ("Kernel regression / Nadaraya-Watson", "nadaraya_watson", [r"kernel|nadaraya|rational.?quadratic"], r"kernel|nadaraya"),
    "mama": ("Ehlers MAMA / FAMA / Hilbert", "extra.mama / extra_ehlers.ehlers_homodyne_dc", [r"\bmama\b|\bfama\b|hilbert", F("computealpha", "hilberttransform", "computecomponent"), TL("MAMA", "HT_TRENDLINE")], r"\bmama\b|hilbert|mesa"),
    "itrend": ("Ehlers Instantaneous Trendline", "itrend", [r"instantaneous|itrend"], r"instantaneous"),
    "median_ma": ("Median", "median", [B("median")], None),
    "gmma": ("Guppy GMMA", "gmma", [r"guppy|gmma"], r"guppy|gmma"),
    "ribbon": ("MA ribbon / multi-MA selector", "ma", [F("ma", "variant", "ma_function", "getma", "f_ma", "f_getmovingaverage", "calc_ma", "ma_selector", "ma_func")], r"ribbon"),
    # --- bands / channels -------------------------------------------------
    "bbands": ("Bollinger Bands", "bbands", [B("bb"), FMZ("BOLL"), TL("BBANDS"), F("bband", "calc_bbupper", "calc_bblower"), r"\b(?:basis|bbbasis|middle)\b.*\n?.*(?:ta\.)?stdev\("], r"bollinger|\bbb\b|\bboll\b"),
    "bbw": ("BB width / %B / squeeze", "bbw / bb_percent_b", [B("bbw"), r"(?:percent_?b|pctb|%b|bbr)\s*=", r"bandwidth"], r"%b|bandwidth|band width"),
    "kc": ("Keltner Channels", "keltner", [B("kc", "kcw"), F("keltner"), r"keltner"], r"keltner"),
    "donchian": ("Donchian / price channel / Ichimoku midline", "donchian", [F("donchian", "f_donchian", "middledonchian", "dchannel", "dchannelalt"), r"donchian"], r"donchian|price channel|turtle"),
    "envelope": ("MA Envelope", "envelope", [r"envelope"], r"envelope"),
    "starc": ("STARC Bands", "starc_bands", [r"starc"], r"starc"),
    "squeeze": ("Squeeze (BB inside KC) / Squeeze Momentum", "squeeze_momentum / ttm_squeeze", [r"sqz|squeeze"], r"squeeze"),
    "lrc": ("Linear regression channel / std-error bands", "extra_tv.linreg_channel / extra_trend.standard_error_bands", [r"(?:linreg|lrc)\w*\s*[\+\-]\s*\w*(?:dev|stdev)", r"regression channel|standard error"], r"regression channel"),
    # --- oscillators ------------------------------------------------------
    "rsi": ("RSI", "rsi", [B("rsi"), FMZ("RSI"), TL("RSI"), F("_rsi", "rsi", "f_rsi")], r"\brsi\b|relative strength index"),
    "stoch": ("Stochastic", "stoch", [B("stoch"), TL("STOCH", "STOCHF"), F("f_stochastic")], r"stoch|\bkd\b"),
    "stochrsi": ("Stochastic RSI", "stoch_rsi", [r"stoch\w*\(\s*(\w*rsi\w*)\s*,\s*\1\s*,\s*\1", TL("STOCHRSI"), F("f_stochrsi", "stochrsi")], r"stoch(?:astic)? ?rsi"),
    "kdj": ("KDJ (Chinese)", "extra.kdj", [FMZ("KDJ"), r"\bkdj\b", r"\bj\s*=\s*3\s*\*\s*k\s*-\s*2\s*\*\s*d\b", F("bcwsma")], r"\bkdj\b"),
    "macd": ("MACD", "macd", [B("macd"), FMZ("MACD"), TL("MACD"), F("calc_macd", "f_macd", "macd")], r"\bmacd\b"),
    "ppo": ("PPO / price oscillator", "ppo / price_oscillator", [r"\bppo\b", TL("PPO", "APO")], r"\bppo\b|price oscillator"),
    "cci": ("CCI", "cci", [B("cci"), TL("CCI")], r"\bcci\b|commodity channel"),
    "wpr": ("Williams %R", "willr", [B("wpr"), TL("WILLR"), r"williams\s*%?r|%r\b"], r"williams ?%?r\b|%r"),
    "mfi": ("MFI", "mfi", [B("mfi"), TL("MFI")], r"\bmfi\b|money flow index"),
    "mom": ("Momentum / ROC", "mom / roc", [B("mom", "roc"), F("momentum", "perc_change"), TL("MOM", "ROC")], r"\broc\b|rate of change"),
    "tsi": ("TSI", "tsi", [B("tsi"), F("double_smooth")], r"\btsi\b|true strength"),
    "cmo": ("CMO", "cmo", [B("cmo"), TL("CMO"), F("getcmo")], r"\bcmo\b|chande momentum"),
    "ao": ("Awesome / Accelerator Oscillator", "awesome_oscillator / accelerator_oscillator", [r"awesome|\bao\s*=\s*(?:ta\.)?sma", F("ac")], r"awesome|accelerator"),
    "uo": ("Ultimate Oscillator", "ultimate_oscillator", [F("uo"), r"ultimate"], r"ultimate oscillator"),
    "fisher": ("Fisher Transform", "fisher", [r"fisher"], r"fisher"),
    "trix": ("TRIX", "trix", [r"\btrix\b", TL("TRIX")], r"\btrix\b"),
    "dpo": ("DPO", "dpo", [r"\bdpo\b|detrended"], r"detrended"),
    "kst": ("KST", "kst", [r"\bkst\b", F("smaroc")], r"\bkst\b|know sure"),
    "coppock": ("Coppock", "coppock", [r"coppock"], r"coppock"),
    "wavetrend": ("WaveTrend", "wavetrend", [r"wavetrend|f_wavetrend", r"\besa\s*=\s*(?:ta\.)?ema\("], r"wave ?trend"),
    "stc": ("Schaff Trend Cycle", "schaff_trend_cycle", [r"\bstc\b|schaff", F("aaaa", "aaaaa")], r"schaff|\bstc\b"),
    "qqe": ("QQE", "qqe", [r"\bqqe\b|RsiMa\b"], r"\bqqe\b"),
    "rvi": ("RVI / RVGI", "rvgi / relative_volatility_index", [r"\brvi\b|\brvgi\b|vigor"], r"\brvi\b|vigor|relative volatility"),
    "smi": ("SMI / SMI Ergodic", "smi / smi_ergodic", [r"\bsmi\b|ergodic"], r"\bsmi\b|ergodic|stochastic momentum"),
    "crsi": ("Connors RSI / RSI2", "connors_rsi", [r"connors|\bcrsi\b", F("updown")], r"connors"),
    "rmi": ("RMI", "rmi", [F("rmi"), r"\brmi\b"], r"\brmi\b|relative momentum"),
    "ifish": ("Inverse Fisher", "inverse_fisher_rsi", [r"inverse.?fisher|ifish"], r"inverse fisher"),
    "elder": ("Elder Ray / Bull-Bear Power / Impulse / Force", "bull_bear_power / elder_impulse / efi", [r"bull\w*power|bear\w*power|elder|force\s*index|\befi\b"], r"elder|bull bear|force index"),
    "demarker": ("DeMarker", "demarker", [r"demarker|demax"], r"demarker"),
    "pmo": ("Price Momentum Oscillator", "pmo", [F("calc_csf"), r"\bpmo\b"], r"price momentum oscillator"),
    "tdi": ("TDI", "tdi", [r"\btdi\b|traders dynamic"], r"traders dynamic|\btdi\b"),
    "ewo": ("Elliott Wave Oscillator", "elliott_wave_oscillator", [r"\bewo\b|elliott"], r"elliott"),
    "bop": ("Balance of Power", "bop", [r"balance.?of.?power|\bbop\b", TL("BOP")], r"balance of power"),
    "cfo": ("Chande Forecast Osc.", "chande_forecast_oscillator", [r"\bcfo\b|forecast oscillator"], None),
    "rci": ("RCI", "rci", [B("rci")], r"\brci\b|rank correlation"),
    "divergence": ("Divergence detection (pivot based)", "extra_tv.divergence", [r"divergence|bulldiv|beardiv|f_finddivs"], r"divergence"),
    # --- trend / volatility ---------------------------------------------
    "atr": ("ATR / TR", "atr / true_range", [B("atr", "tr"), V("tr"), FMZ("ATR"), TL("ATR", "NATR", "TRANGE"), F("atr", "atr_func", "true_range")], r"\batr\b|average true range"),
    "dmi": ("DMI / ADX (Wilder, TV)", "dmi / adx", [B("dmi", "adx"), F("dirmov", "adxdirmov"), TL("ADX", "PLUS_DI", "MINUS_DI", "ADXR")], r"\badx\b|\bdmi\b|directional"),
    "adx_sma": ("ADX = SMA(DX) variant (BeikabuOyaji)", "extra.adx_sma", [r"adx\w*\s*=\s*(?:ta\.)?sma\(\s*dx", F("calcadx_masanakamura")], None),
    "supertrend": ("Supertrend", "supertrend / supertrend_kivanc", [B("supertrend"), F("supertrend", "f_supertrend", "pine_supertrend", "f_getsupertrend"), r"supertrend"], r"super ?trend"),
    "psar": ("Parabolic SAR", "psar", [B("sar"), TL("SAR")], r"parabolic|\bsar\b"),
    "ichimoku": ("Ichimoku", "ichimoku", [r"tenkan|kijun|senkou|ichimoku|conversionLine"], r"ichimoku"),
    "aroon": ("Aroon", "aroon", [r"\baroon", TL("AROON")], r"\baroon"),
    "chop": ("Choppiness / Chop Zone", "choppiness / chop_zone", [r"choppiness|\bchop\w*\s*="], r"chop"),
    "vortex": ("Vortex", "vortex", [r"vortex|\bvip\b|\bvim\b"], r"vortex"),
    "chandelier": ("Chandelier Exit", "chandelier_exit", [r"chandelier|longStopPrev"], r"chandelier"),
    "utbot": ("UT Bot", "ut_bot", [r"xATRTrailingStop|ut.?bot"], r"ut bot"),
    "halftrend": ("HalfTrend", "halftrend", [r"halftrend|half.?trend"], r"half ?trend"),
    "ssl": ("SSL Channel", "ssl_channel", [r"\bssl\w*|\bhlv\b"], r"\bssl\b"),
    "rangefilter": ("Range Filter / Twin Range Filter", "range_filter / twin_range_filter", [F("rngfilt", "smoothrng", "range_filter", "rng_filt", "rng_size")], r"range filter"),
    "trendmagic": ("Trend Magic", "trend_magic", [r"magictrend|trend.?magic"], r"trend magic"),
    "alphatrend": ("AlphaTrend", "alphatrend", [r"alphatrend"], r"alpha ?trend"),
    "ott": ("OTT / PMax / VAR-based trackers", "ott", [r"\bott\b|\bpmax\b|optimized trend"], r"\bott\b|pmax|optimized trend"),
    "vstop": ("Volatility Stop", "volatility_stop", [F("volstop"), r"vstop|volatility.?stop"], r"volatility stop"),
    "cks": ("Chande Kroll Stop", "chande_kroll_stop", [r"kroll"], r"kroll"),
    "atrstop": ("ATR trailing stop (generic)", "atr_stop_loss", [r"atr\w*\s*\*\s*\w*mult\w*.*\n?.*(?:trail|stop)"], r"atr (?:trailing|stop)"),
    "hv": ("Historical volatility / stdev", "historical_volatility / stdev", [B("stdev", "variance", "dev"), TL("STDDEV", "VAR"), r"historical.?volatility"], r"volatility"),
    "heikin": ("Heikin Ashi", "heikin_ashi", [r"heikinashi|haclose|ha_close|haopen"], r"heikin|ashi"),
    "renko": ("Renko bricks", "extra_trend.renko", [r"renko"], r"renko"),
    "wvf": ("Williams Vix Fix", "williams_vix_fix", [r"\bwvf\b|vix.?fix"], r"vix fix"),
    "wae": ("Waddah Attar Explosion", "waddah_attar_explosion", [r"explosion|deadzone|waddah"], r"waddah"),
    "coral": ("Coral Trend", "coral", [r"coral"], r"coral"),
    "mavilimw": ("MavilimW", "mavilimw", [r"mavilim|mavw"], r"mavilim"),
    # --- volume -----------------------------------------------------------
    "obv": ("OBV", "obv", [V("obv"), FMZ("OBV"), TL("OBV"), r"\bobv\b"], r"\bobv\b|on balance"),
    "vwap": ("VWAP", "vwap / rolling_vwap", [B("vwap"), V("vwap"), r"\bvwap\b"], r"vwap"),
    "ad": ("Accumulation/Distribution / CMF / Chaikin", "accdist / cmf / chaikin_osc", [V("accdist"), FMZ("CMF"), TL("AD", "ADOSC"), r"\bcmf\b|chaikin"], r"chaikin|accumulation|\bcmf\b"),
    "pvt": ("PVT / NVI / PVI / Williams AD", "pvt / nvi / pvi / williams_ad", [V("pvt", "nvi", "pvi", "wad", "wvad", "iii")], None),
    "volosc": ("Volume oscillator / RVOL / volume MA", "relative_volume / ppo", [r"(?:ta\.)?(?:sma|ema)\(\s*volume\s*,"], r"volume"),
    "vfi": ("VFI / Klinger / EOM / VZO", "vfi / klinger / ease_of_movement / volume_zone_oscillator", [r"\bvfi\b|klinger|\bkvo\b|ease.?of.?move|\beom\b|\bvzo\b"], r"klinger|ease of movement|volume flow"),
    "mfi_bw": ("Bill Williams (Alligator, Fractals, Gator, MFI)", "alligator / fractals / gator", [FMZ("Alligator"), r"alligator|\bjaw\b|\bteeth\b|\blips\b", F("f_top_fractal", "f_bot_fractal", "f_fractalize", "isbwfractal", "isregularfractal", "fractalup", "fractaldn"), r"fractal"], r"alligator|fractal|bill williams"),
    # --- structure / levels / helpers --------------------------------------
    "highest": ("Highest / Lowest", "highest / lowest (kernels)", [B("highest", "lowest", "highestbars", "lowestbars"), FMZ("Highest", "Lowest"), r"\b(?:HHV|LLV|HV|LV)\s*\("], r"high low|breakout"),
    "pivots_hl": ("Pivot high / low (swing points)", "extra_tv.pivothigh / pivotlow", [B("pivothigh", "pivotlow")], r"swing|pivot"),
    "pivot_levels": ("Pivot point levels (P, R1, S1...)", "pivot_points", [r"\b[RS][123]\s*=\s*.*\b(?:pp|pivot|P)\b", r"camarilla|woodie|pivot.?point"], r"pivot point|camarilla"),
    "zigzag": ("ZigZag", "extra_tv.zigzag", [F("zigzag", "f_zz"), r"zigzag"], r"zig ?zag"),
    "fib": ("Fibonacci levels", "extra.fib_levels", [r"\bfib\w*\s*=|0\.618|0\.382"], r"fibonacci|retracement"),
    "percentile": ("Percentile / percent rank", "percentrank", [B("percentrank", "percentile_linear_interpolation", "percentile_nearest_rank")], r"percentile"),
    "zscore": ("Z-score", "zscore", [r"z_?score"], r"z.?score"),
    "correlation": ("Correlation / beta", "correlation / beta", [B("correlation"), r"\bbeta\b"], r"correlation"),
    "slope": ("Linear regression slope / angle", "linreg", [F("calcslope", "f_angle", "angle", "getlookbackslope"), TL("LINEARREG_SLOPE"), r"\bslope\b"], r"slope|angle"),
    "candles": ("Candlestick patterns", "extra_tv.candlestick_patterns", [F("isbullishengulfing", "isbearishengulfing", "ishammer", "isdoji", "isshootingstar", "isengulfing", "ispinbar", "ishangingman", "isinvertedhammer", "isthreewhitesoldiers", "is3lsbull", "is3lsbear"), TL("CDL\\w+")], r"engulfing|hammer|doji|pin bar|candlestick|harami"),
    "rev123": ("123 Reversal (HPotter, stochastic based)", "extra.reversal_123", [F("reversal123")], r"123 reversal"),
    "mtf": ("Higher-timeframe values (security)", "extra_tv.htf / resample_ohlcv", [r"\b(?:request\.)?security\s*\("], r"timeframe|mtf"),
}


def compile_all():
    out = {}
    for key, (label, fn, pats, tpat) in D.items():
        rx = [re.compile(p, re.I | re.M) for p in pats]
        trx = re.compile(tpat, re.I) if tpat else None
        out[key] = (label, fn, rx, trx)
    return out


def main(code_json, out_json):
    data = json.load(open(code_json))
    titles = {}
    for lang, rows in data.items():
        for f, _ in rows:
            titles[f] = f
    det = compile_all()
    usage = {k: {"label": v[0], "tv": v[1], "files": [], "title_only": []} for k, v in det.items()}
    per_file = {}
    for lang, rows in data.items():
        for f, code in rows:
            tags = []
            for key, (label, fn, rx, trx) in det.items():
                if any(r.search(code) for r in rx):
                    usage[key]["files"].append(f)
                    tags.append(key)
                elif trx is not None and trx.search(f.replace("-", " ")):
                    usage[key]["title_only"].append(f)
            per_file[f] = {"lang": lang, "tags": tags}
    json.dump({"usage": usage, "per_file": per_file}, open(out_json, "w"), ensure_ascii=False)
    total = len(per_file)
    print(f"{total} strategies")
    for key, u in sorted(usage.items(), key=lambda kv: -len(kv[1]["files"])):
        print(f"{len(u['files']):5d} {len(u['title_only']):4d}  {key:14s} {u['label']}  -> {u['tv']}")
    none = [f for f, v in per_file.items() if not v["tags"]]
    print("files with no tag:", len(none))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
