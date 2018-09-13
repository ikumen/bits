/**
 * Very naive console wrapper.
 */
function noOp() {}

export default (function(){
    const logger = {
        debug: noOp,
        error: noOp,
        warn: noOp,
        info: noOp
    }

    if (window.location && console) {
        logger.error = console.error;
        logger.warn = console.warn;
        if (window.location.hostname === 'localhost') {
            logger.debug = console.debug;
            logger.info = console.info;
        }
    }

    return logger;
})();