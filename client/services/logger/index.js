/**
 * Very naive console wrapper.
 */
function _noOp() {}
function _logWithCaller(log, ...args) {
    var callerName;
    try { throw new Error(); }
    catch (e) { 
        var re = /(\w+)@|at (\w+)\.?(_?\w+\$?) \(/g, st = e.stack, m;
        re.exec(st), // skip this wrapper/callback
        m = re.exec(st);
        //console.log(m)
        callerName = m[2] + (m[3] ? '.' + m[3] : '') + '(): ';
    }
    log(callerName, ...args)
}

export default (function(){
    const logger = {
        debug: _noOp,
        error: _noOp,
        warn: _noOp,
        info: _noOp
    }

    if (window.location && console) {
        logger.error = console.error;
        logger.warn = console.warn;
        if (window.location.hostname === 'localhost') {
            logger.debug = (...args) => {_logWithCaller(console.debug, ...args)}
            logger.info = (...args) => {_logWithCaller(console.info, ...args)}
        }
    }

    return logger;
})();