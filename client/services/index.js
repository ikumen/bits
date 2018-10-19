class FetchError extends Error {
    constructor(status, ...params) {
        super(...params);
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, FetchError);
        }
        this.status = status;
        this.params = params;
    }
}

class AppError extends Error {
    constructor(status, message, ...args) {
        super(...args);
        if (Error.captureStackTrace) { Error.captureStackTrace(this, AppError); }
        this.status = status;
        this.message = message;
    }
}

class NotFoundError extends AppError {
    constructor(...args) {
        super(...args);
        if (Error.captureStackTrace) { Error.captureStackTrace(this, NotFoundError); }
    }
}

class AuthenticationError extends AppError {
    constructor(...args) {
        super(...args);
        if (Error.captureStackTrace) { Error.captureStackTrace(this, AuthenticationError); }
    }
}


class Service {
    constructor() {
        // for this reference back to this.reject
        this.status = this.status.bind(this);
    }

    getJSONHeaders() {
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }

    reject(error) {
        return Promise.reject(error);
    }

    status(resp) {
        const {status, statusText} = resp;
        if (status >= 200 && status < 300) 
            return Promise.resolve(resp);
        if (status == 401 || status == 403)
            return this.reject(new AuthenticationError(status, statusText));
        if (status == 404) 
            return this.reject(new NotFoundError(status, statusText));
        return this.reject(new AppError(status, statusText))
    }

    json(resp) {
        return resp.json();
    }
}

export {Service, NotFoundError, AppError, AuthenticationError};