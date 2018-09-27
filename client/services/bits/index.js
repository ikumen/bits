import Log from '../logger';
import Service from '../../services';

class BitService extends Service {

    async list(userId) {
        Log.info('Get all bits');
        return await fetch('/api/@' + userId + '/bits')
            .then(this.status)
            .then(this.json)
            .catch(err => Log.error(err));
    }

    async get(bitId) {
        Log.info('Get bit', bitId)
        return await fetch('/api/bits/' + bitId)
            .then(this.status)
            .then(this.json)
            .catch(err => Log.error(err));
    }

    async create(userId) {
        Log.info('Creating new bit!')
        return await fetch('/api/bits', {
                method: 'POST',
                body: JSON.stringify({}),
                headers: this.getJSONHeaders()})
            .then(this.status)
            .then(this.json)
            .catch(err => Log.error(err));
    }

    async update(id, data) {
        Log.info('Save bit', id, data)
        return await fetch('/api/bits/' + id, {
                method: 'PATCH',
                body: JSON.stringify(data),
                headers: this.getJSONHeaders()})
            .then(this.status)
            .catch(err => Log.error(err));
    }

    async delete(bitId) {
        Log.info('Deleting bit', bitId);
        return await fetch('/api/bits/' + bitId, {
                method: 'DELETE',
                headers: this.getJSONHeaders()})
            .then(this.status)
            .catch(err => Log.error(err));
    }
}

export default new BitService();