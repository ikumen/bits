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
        return <Page className="about">
            <p>
            Welcome to Bits, my no frills <a href="https://gist.github.com/">Gist</a> powered blog. It's 
            an <a href="https://github.com/ikumen/bits">ongoing project</a> that I use to learn Python and React. 
            You're welcome to give it a try or <a href="https://github.com/ikumen/bits">fork it</a> for yourself. 
            </p>
            <p>
            It has the following features:

            <ul>
                <li>distraction free&mdash;simple plain text editor with support for markdown</li>
                <li>for introverts&mdash;no social media baggage, nothing to share, favorite, or @mention</li>
                <li>all your bits belong to us, not really they are saved to your Gist account, your own them</li>
            </ul>
            
            To get started, all you need is a <a href="https://github.com">GitHub</a> account and a little <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet">knowledge of Markdown</a>. 
            Sign in when you're ready.
            </p>
        </Page>
    }
}

export default AboutPage;