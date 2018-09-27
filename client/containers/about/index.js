import React from 'react';
import UserService from '../../services/user';
import {Page} from '../../components/layouts';

class AboutPage extends React.Component {
    constructor(props) {
        super(props);
        this.onCurrentUserLoaded = this.onCurrentUserLoaded.bind(this);
        this.state = {
            showSignin: false
        }
    }

    componentDidMount() {
        UserService.getCurrentUser()
            .then(this.onCurrentUserLoaded);
    }

    onCurrentUserLoaded(user) {
        if (user) {
            this.setState({showSignin: true});
        }
    }

    render() {
        return <Page>
            <h2>Welcome to Bits!</h2>
            <p>Bits is a <a href="https://gist.github.com/">Gist</a> powered microblog.
         
            All you need to get started is a <a href="https://github.com">GitHub</a> account and 
            a little <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet">knowledge of Markdown</a>.</p>
        </Page>
    }
}

export default AboutPage;