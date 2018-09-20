import Log from '../logger';

const HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

const DEFAULTS = {
    description: 'Enter description here',
    content: 'Enter markdown here',
}

class BitService {

    async list(userId) {
        Log.info('Get all bits');
        let resp = await fetch('/api/@' + userId + '/bits');
        return await resp.json(); 
    }

    async get(bitId) {
        Log.info('Get bit', bitId)
        let resp = await fetch('/api/bits/' + bitId);
        return await resp.json();
    }

    async create() {
        Log.info('Creating new bit!')
        let resp = await fetch('/api/bits', {
            method: 'POST',
            body: JSON.stringify({
                description: DEFAULTS.description,
                content: DEFAULTS.content,
                published: false,
                published_at: '',
                tags: []
            }),
            headers: HEADERS
        });
        return await resp.json();
    }

    async update(bit) {
        Log.info('Save bit', bit)
        let resp = await fetch('/api/bits/' + bit._id, {
            method: 'PATCH',
            body: JSON.stringify(bit),
            headers: HEADERS
        });
        return await resp.json();
    }

    async delete(bitId) {
        Log.info('Deleting bit', bitId);
        let resp = await fetch('/api/bits/' + bitId, {
            method: 'DELETE',
            headers: HEADERS
        });
        return await resp.json();
    }
}

export default new BitService();