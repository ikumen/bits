import React from 'react';

class BitList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            bits: []
        }
    }

    async fetchBits() {
        let resp = await fetch('/api/u:' + this.props.user + '/bits');
        return await resp.json();
    }

    componentDidMount() {
        this.fetchBits()
            .then(bits => this.setState({bits: bits}))
            .catch(err => console.log(err))
    }

    render() {
        const bits = this.state.bits;
        return <ul>
            {bits.map((bit, i) => {
                const b = bit.files['README.md']
                return <li key={bit._id}>{bit.description}</li>
            })}
        </ul>
    }
}

export default BitList;