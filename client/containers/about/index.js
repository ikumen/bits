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
            <h1></h1>
            <section>
            Welcome to Bits, my no frills <a href="https://gist.github.com/">Gist</a> powered blog. It's 
            an <a href="https://github.com/ikumen/bits">ongoing project</a> that I use to learn Python and React. 
            You're welcome to give it a try or <a href="https://github.com/ikumen/bits">fork it</a> for yourself. 
            </section>
            <section>
            It has the following features:

            <ul>
                <li>distraction free, simple plain text editor with support for markdown</li>
                <li>for introverts, no social media baggage</li>
                <li><a href="https://en.wikipedia.org/wiki/All_your_base_are_belong_to_us">all your bits belong to us</a>, just kidding, the Gist are under your account</li>
            </ul>
            
            To get started, all you need is a <a href="https://github.com">GitHub</a> account and a little <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet">knowledge of Markdown</a>. 
            Sign in when you're ready.
            </section>
        </Page>
    }
}

export default AboutPage;