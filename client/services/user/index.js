import Log from '../logger';

class UserService {
    constructor() {
        this.getCurrentUser = this.getCurrentUser.bind(this);
        this.atUsers = {}
    }

    async getCurrentUser() {
        if (!this.user) {
            Log.info('Fetching user from backend!')
            this.user = await fetch('/api/user')
                .then(this.parseResponse)
                .catch(err => err.status == 401 ? false : err)
                .catch(this.onError);
        }
        return this.user;
    }

    async getAtUser(userId) {
        if (!this.atUsers[userId]) {
            this.atUsers[userId] = await fetch('/api/@' + userId)
                .then(this.parseResponse)
                .catch(this.onError);
        }
        return this.atUsers[userId];
    }

    async parseResponse(resp) {
        return await resp.json();
    }

    onError(err) {
        Log.info(err);
        return err;
    }
}

export default new UserService();