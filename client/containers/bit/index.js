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
        console.log(props)
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

        this.state = {
            atUserId: props.match.params.userId,
            bitId: props.match.params.bitId
        }
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
                viewOnly={!user.authenticated}
            /> 
        });
    }

    render() {
        return <Page>
            {this.state.editor}
        </Page>
    }
}

export {BitPage, CreateBitPage};
