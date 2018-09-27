class FetchError extends Error {
    constructor(status, ...params) {
        super(...params);
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, FetchError);
        }
        this.status = status;
    }
}

class Service {
    getJSONHeaders() {
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

    status(resp) {
        if (resp.status >= 200 && resp.status < 300) {
            return Promise.resolve(resp);
        } else {
            return Promise.reject(new FetchError(resp.status, resp.statusText))
        }
    }

    json(resp) {
        return resp.json();
    }
}

export default Service;