import React from 'react';
import UserService from '../../services/user';

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
        if (!user.authenticated) {
            this.setState({showSignin: true});
        }
    }

    render() {
        return <div className="about">
            <h2>Welcome to Bits!</h2>
            <p>Bits is a simple microblog for keeping notes without all the social baggage.
            There are no complicated editors to distract or get in your way, just <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet">simple plain text Markdown</a>.
            </p>
        
            <p><a href="/signin">Signin to get started</a>, all you need is a <a href="https://github.com">GitHub</a> account and a little knowledge of Markdown.</p>
        </div>
    }
}

export default AboutPage;