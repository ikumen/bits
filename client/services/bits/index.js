import Log from '../logger';

const HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

class BitService {

    async list(userId) {
        Log.info('Get all bits');
        let resp = await fetch('/api/@' + userId + '/bits');
        return await resp.json(); 
    }

    async get(userId, bitId) {
        Log.info('Get bit', bitId)
        let resp = await fetch('/api/@' + userId + '/bits/' + bitId);
        return await resp.json();
    }

    async create(userId) {
        Log.info('Creating new bit!')
        let resp = await fetch('/api/@' + userId + '/bits', {
            method: 'POST',
            body: JSON.stringify({
                description: '_', 
                content: '_',
                tags: [],
                published: false,
                published_at: ''
            }),
            headers: HEADERS
        });
        return await resp.json();
    }

    async save(userId, bit) {
        Log.info('Save bit', bit)
        let resp = await fetch('/api/@' + userId + '/bits', {
            method: 'PUT',
            body: JSON.stringify(bit),
            headers: HEADERS
        });
        return await resp.json();
    }
}

export default new BitService();