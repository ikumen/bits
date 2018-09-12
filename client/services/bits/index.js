class BitService {
    
    async list(userId) {
        let resp = await fetch('/api/@' + userId + '/bits');
        return await resp.json(); 
    }

    async get(userId, bitId) {
        let resp = await fetch('/api/@' + userId + '/bits/' + bitId);
        return await resp.json();
    }
}

export default new BitService();