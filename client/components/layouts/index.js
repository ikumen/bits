import React from 'react';
import UserService from '../../services/user';

const Footer = () => (
    <footer>
        <div className="copyright">
            &copy; {new Date().getFullYear()} Thong Nguyen
        </div>
        <div className="contact">
            <a href="https://github.com/ikumen/bits"><i className="icon-github-circled" title="projects"></i></a>
            <a href="https://github.com/ikumen/bits/issues">Contact</a>
            <a href="/about">About</a>
        </div>
    </footer>
)

class Header extends React.Component {
    constructor(props) {
        super(props);

        this.onCurrentUserLoaded = this.onCurrentUserLoaded.bind(this);
        this.state = {
            user: false
        }

        UserService.getCurrentUser()
            .then(this.onCurrentUserLoaded);
    }

    onCurrentUserLoaded(user) {
        if (user.authenticated) {
            this.setState({user: user});
        }
    }

    render() {
        return <header>
            <div className="logo"><a href={this.state.user ? '/@' + this.state.user.user_id : '/'}><i className="icon-doc-text"></i> Bits</a></div>
            <div className="signin">
                {this.state.user ? 
                    <a href="/signout">Sign out</a> 
                    :
                    <a href="/signin">Sign in</a>
                }
            </div>
        </header>        
    }
}

export {Footer, Header};