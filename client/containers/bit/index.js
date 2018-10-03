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
        this.switchMode = this.switchMode.bind(this);

        this.state = {
            atUserId: props.match.params.atUserId,
            bitId: props.match.params.bitId,
            editMode: props.match.params.edit === 'edit'
        }
    }

    componentDidUpdate(prevProps) {
        if (prevProps.match.params.bitId != this.props.match.params.bitId) {
            const {atUserId, bitId} = this.props.match.params;
            this.setState({atUserId: atUserId, bitId: bitId, editMode: this.props.match.params.edit === 'edit'});
            this.loadBit(atUserId, bitId);
        } else if (prevProps.match.params.edit !== this.props.match.params.edit) {
            this.setState({editMode: this.props.match.params.edit === 'edit'})
        }        
    }

    loadBit(atUserId, bitId) {
        Promise.all([
                UserService.getAtUser(atUserId),
                BitService.get(bitId)])
            .then(([atUser, bit]) => this.setState({atUser: atUser, bit: bit}))
            .catch(err => Log.error(err));
    }

    switchMode() {
        const viewUrl = '/@' + this.state.atUserId + '/bits/' + this.state.bitId;
        if (this.state.editMode) {
            this.props.history.push(viewUrl)
        } else {
            this.props.history.push(viewUrl + '/edit')
        }
    }

    componentDidMount() {
        this.loadBit(this.state.atUserId, this.state.bitId);
    }

    onDelete() {
        BitService.delete(this.state.bit.id)
            .then(() => this.props.history.replace('/@' + this.state.atUserId))
            .catch(err => Log.error(err))
    }

    render() {
        return <Page>
            {this.state.atUser && 
                <Editor bit={this.state.bit} 
                    onDelete={this.onDelete} 
                    atUser={this.state.atUser} 
                    editMode={this.state.editMode && this.state.atUser.is_auth}
                    switchMode={this.switchMode}
                />
            }
        </Page>
    }
}

export {BitPage, CreateBitPage};
