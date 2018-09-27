import Log from '../logger';
import Service from '../../services';

class UserService extends Service {
    constructor() {
        super()
        this.getCurrentUser = this.getCurrentUser.bind(this);
        this.atUsers = {}
    }

    async getCurrentUser() {
        if (!this.user) {
            Log.info('Fetching user from backend!')
            return await fetch('/api/user')
                .then(this.status)
                .then(this.json)
                .catch(err => Log.error(err));
        }
        return this.user;
    }

    async getAtUser(userId) {
        if (!this.atUsers[userId]) {
            return await fetch('/api/@' + userId)
                .then(this.status)
                .then(this.json)
                .then(user => {
                    this.atUsers[userId] = user;
                    return user;
                })
                .catch(err => Log.error(err));
        }
        return this.atUsers[userId];
    }
}

export default new UserService();