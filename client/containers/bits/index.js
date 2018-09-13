import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import Editor from '../../components/editor';
import UserService from '../../services/user';


const BitList = styled.ul`
`;

const Bit = styled.li`
`;


class BitPage extends React.Component {
    constructor(props) {
        super(props);
        this.onCurrentUserLoaded = this.onCurrentUserLoaded.bind(this);

        this.state = {
            userId: props.match.params.userId,
            bitId: props.match.params.bitId,
            viewOnly: true
        }

        UserService.getCurrentUser()
            .then(this.onCurrentUserLoaded)
    }

    onCurrentUserLoaded(user) {
        if (user.authenticated) {
            this.setState({viewOnly: false});
        }
    }

    render() {
        return <Editor {...this.state} />
    }
}


class BitIndexPage extends React.Component {
    constructor(props) {
        super(props);
        this.onBitsLoaded = this.onBitsLoaded.bind(this);
        this.state = {
            userId: (props.match.params.userId || '') // TODO: should error if no user
        }
    }

    componentDidMount() {
        BitService.list(this.state.userId)
            .then(this.onBitsLoaded)
            .catch(err => console.log(err));
    }

    onBitsLoaded(bits) {
        this.setState({bits: bits.map((bit, i) => {
            return <Bit key={i}>
                <Link to={{
                    pathname: "/@" + this.state.userId + '/bits/' + bit._id,
                }}>{bit.description}
                </Link>
            </Bit>
        })});
    }

    render() {
        return <BitList>
            {this.state.bits}
        </BitList>
    }
 }

export {BitPage, BitIndexPage};