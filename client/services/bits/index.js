import Log from '../logger';
import {Service} from '../../services';

class BitService extends Service {

    async list(userId) {
        Log.info('Get all bits');
        return await fetch('/api/@' + userId + '/bits')
            .then(this.status)
            .then(this.json);
    }

    async get(userId, bitId) {
        Log.info('Get bit', bitId)
        return await fetch('/api/@' + userId + '/bits/' + bitId)
            .then(this.status)
            .then(this.json);
    }

    async create(userId) {
        Log.info('Creating new bit!')
        return await fetch('/api/@' + userId + '/bits', {
                method: 'POST',
                body: JSON.stringify({}),
                headers: this.getJSONHeaders()})
            .then(this.status)
            .then(this.json);
    }

    async update(userId, bitId, data) {
        Log.info('Save bit', bitId, data)
        return await fetch('/api/@' + userId + '/bits/' + bitId, {
                method: 'PATCH',
                body: JSON.stringify(data),
                headers: this.getJSONHeaders()})
            .then(this.status);
    }

    async delete(userId, bitId) {
        Log.info('Deleting bit', bitId);
        return await fetch('/api/@' + userId + '/bits/' + bitId, {
                method: 'DELETE',
                headers: this.getJSONHeaders()})
            .then(this.status);
    }
}

export default new BitService();