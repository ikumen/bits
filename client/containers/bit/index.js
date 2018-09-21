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
        
        this.onAtUserLoaded = this.onAtUserLoaded.bind(this);
        this.onDeleteComplete = this.onDeleteComplete.bind(this);

        this.state = {
            atUserId: props.match.params.userId,
            bitId: props.match.params.bitId
        }
    }

    componentDidUpdate(prevProps) {
        console.log('did update in bitpage', this.props)
    }

    componentDidMount() {
        UserService.getAtUser(this.state.atUserId)
            .then(this.onAtUserLoaded)
            .catch(err => Log.error(err));        
    }

    onAtUserLoaded(user) {
        this.setState({
            atUser: user,
            editor: <Editor 
                bitId={this.state.bitId} 
                user={user} 
                onDeleteComplete={this.onDeleteComplete}
                viewOnly={!user.authenticated}
            /> 
        });
    }

    onDeleteComplete() {
        this.props.history.replace('/@' + this.state.atUserId)
    }

    render() {
        return <Page>
            {this.state.editor}
        </Page>
    }
}

export {BitPage, CreateBitPage};
