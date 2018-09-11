import React from 'react';
import BitService from '../../services/bits';
import {Link} from 'react-router-dom';
import styled from 'styled-components';

const BitList = styled.ul`
`;

const Bit = styled.li`
`;

class BitPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            userId: props.match.params.userId,
            bitId: props.match.params.bitId,
            bit: {content: ''},
        }
    }

    componentDidMount() {
        BitService.get(this.state.userId, this.state.bitId)
            .then(bit => 
                this.setState({bit: {
                    content: bit['files']['README.md']['content']
                }}))
            .catch(err => console.log(err));
    }

    render() {
        const bit = this.state.bit;
        return <div>
            {bit.content}
        </div>
    }
}


class BitIndexPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            userId: (props.match.params.userId || '') // TODO: should error if no user
        }
    }

    componentDidMount() {
        BitService.list(this.state.userId)
            .then(bits => {
                this.setState({bits: bits.map((bit, i) => {
                    return <Bit key={i}>
                        <Link to={{
                            pathname: "/u:" + this.state.userId + '/bits/' + bit._id,
                        }}>{bit.description}
                        </Link>
                    </Bit>
                })});
            })
            .catch(err => console.log(err));
    }

    render() {
        return <BitList>
            {this.state.bits}
        </BitList>
    }
 }

export {BitPage, BitIndexPage};