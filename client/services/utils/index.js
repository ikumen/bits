export default (function() {
    return {
        formatDateString: function(s, opts) {
            if (s != null && s !== undefined && s !== '') {
                const d = new Date(s);
                const mon = d.getMonth()+1;
                const day = d.getDate();
                return d.getFullYear() + '-' + 
                    (mon < 10 ? '0' : '') + mon + '-' +
                    (day < 10 ? '0' : '') + day;
            } else {
                return opts && opts.default ? opts.default : '';
            }
        }
    }
})();