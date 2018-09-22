import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Editor from '../../components/editor';
import Log from '../../services/logger';
import {Page} from '../../components/layouts';


class CreateBitPage extends React.Component {
    constructor(props) {
        super(props);
    }
    createNewBit(evt) {
        if (this.state.user) {
            BitService.create()
                .then(this.onCreateNewBit)
                .catch(err => Log.error(err));
        } else {
            //TODO: signout
        }
    }

    onCreateNewBit(bit) {
        Log.debug('Created bit:', bit);
        const url = '/@' + this.state.user._id + '/bits/' + bit._id;
        this.props.history.push(url);
    }


    render() {
        return <Page>
            <div>
                Creating new Bit ...
            </div>
        </Page>
    }
}

class BitPage extends React.Component {
    constructor(props) {
        super(props);
        
        this.onDelete = this.onDelete.bind(this);
        this.onBitLoaded = this.onBitLoaded.bind(this);

        this.state = {
            atUserId: props.match.params.userId,
            bitId: props.match.params.bitId
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.match.params.bitId != this.props.match.params.bitId) {
            const {userId, bitId} = this.props.match.params;
            this.setState({atUserId: userId, bitId: bitId});
            this.loadBit(userId, bitId);
        }
    }

    loadBit(userId, bitId) {
        BitService.get(userId, bitId)
            .then(this.onBitLoaded)
            .catch(err => Log.error(err));
    }

    componentDidMount() {
        this.loadBit(this.state.atUserId, this.state.bitId);
    }

    onBitLoaded(resp) {
        const {bits, ...atUser} = resp;
        this.setState({bit: bits[0], atUser: atUser});
    }

    onDelete() {
        BitService.delete(this.state.atUser._id, this.state.bit._id)
            .then(() => this.props.history.replace('/@' + this.state.atUserId))
            .catch(err => Log.error(err))
    }

    render() {
        return <Page>
            {this.state.atUser && <Editor bit={this.state.bit} onDelete={this.onDelete} atUser={this.state.atUser} />}
        </Page>
    }
}

export {BitPage, CreateBitPage};
