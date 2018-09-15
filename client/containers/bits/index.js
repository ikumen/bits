import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import Editor from '../../components/editor';
import UserService from '../../services/user';
import Log from '../../services/logger';


const BitList = styled.ul`
    padding: 0;
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
        this.onCreateBitComplete = this.onCreateBitComplete.bind(this);
        this.buildBitUrl = this.buildBitUrl.bind(this);
        this.createNewBit = this.createNewBit.bind(this);
        this.state = {
            userId: (props.match.params.userId || '') // TODO: should error if no user
        }
    }

    componentDidMount() {
        BitService.list(this.state.userId)
            .then(this.onBitsLoaded)
            .catch(err => Log.error(err));
    }

    createNewBit() {
        BitService.create(this.state.userId)
            .then(this.onCreateBitComplete)
            .catch(err => Log.error(err));
    }

    onCreateBitComplete(bit) {
        Log.debug('Created bit:', bit);
        if (bit._id) {
            const bitUrl = this.buildBitUrl(this.state.userId, bit._id);
            Log.debug('Redirecting to ...', bitUrl);
            this.props.history.push(bitUrl);
        } else {
            //TODO: handle
        }
    }

    buildBitUrl(userId, bitId) {
        return '/@' + userId + '/bits/' + bitId;
    }

    onBitsLoaded(bits) {
        this.setState({bits: bits.map((bit, i) => {
            return <Bit key={i}>
                <Link to={{
                    pathname: this.buildBitUrl(this.state.userId, bit._id),
                }}>{bit.description || bit._id}
                </Link>
            </Bit>
        })});
    }

    render() {
        return <BitList>
            <div className="toolbar">
                <button onClick={this.createNewBit}>Create new Bit</button>
            </div>
            {this.state.bits}
        </BitList>
    }
 }

export {BitPage, BitIndexPage};