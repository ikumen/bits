import Log from '../logger';

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

    async save(userId, bit) {
        Log.info('Save bit', bit)
        let resp = await fetch('/api/@' + userId + '/bits', {
            method: 'POST',
            body: JSON.stringify(bit),
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        });
        return await resp.json();
    }
}

export default new BitService();