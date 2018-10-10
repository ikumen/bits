export default (function() {
    return {
        toSimpleISOFormat(date) {
            const d = this.toFullISOFormat(date);
            if (d === NaN)
                return d;
            return d.substring(0, 10);

        },
        toFullISOFormat(date) {
            const d = Date.parse(date);
            if (isNaN(d))
                return d;
            return new Date(d).toISOString();
        },
        isValidDate(d, f) {
            if (isNaN(new Date(d)))
                return false;
            const re = /(\d{4})-(\d{2})-(\d{2})/;
            const m = re.exec(d);
            return m && m.length == 4;
        },
        flattenArray(arr) {
            return Array.isArray(arr) ? arr.join(', ') : arr;
        },
        arraysAreEqual(a1, a2) {
            if (!Array.isArray(a1) || !Array.isArray(a2)) return false;
            return a1.join() === a2.join();
        }
    }
})();