import Log from '../logger';

class UserService {
    constructor() {
        this.getCurrentUser = this.getCurrentUser.bind(this);
    }

    async getCurrentUser() {
        if (!this.user) {
            Log.info('Fetching user from backend!')
            this.user = fetch('/api/user')
                .then(this.praseResponse)
                .catch(this.onError);
        }
        return this.user;
    }

    praseResponse(resp) {
        return resp.json();
    }

    onError(err) {
        Log.info(err);
        return err;
    }
}

export default new UserService();