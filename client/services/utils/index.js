export default (function() {
    return {
        formatDateString: function(s) {
            const d = new Date(s);
            return d.getFullYear() + '-' + (d.getMonth()+1) + '-' + d.getDate();
        }
    }
})();