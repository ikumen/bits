import React from 'react';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import BitService from '../../services/bits';
import Log from '../../services/logger';
import styled from 'styled-components';

const SubHeader = styled.div`
    display: flex;
    flex-direction: row;
    align-items: center;
`;

const Page = styled.div`
    width: 100%;
    padding: 0;
    margin: 80px auto 0;
    flex: 1;
`;

const StyledHeader = styled.div`
    z-index: 1;
    padding: 10px 0; 
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: #20232a;

    header {
        margin-left: auto;
        margin-right: auto;
        max-width: 980px;
        width: 90%;
        display: flex;
        flex-direction: row;
        align-items: center;        
    }
    header a, header a:hover {
        color: #ffffff;
        text-decoration: none;
    }
    header .logo, header .signin {
        flex: 1;
        font-size: .8rem;
        font-weight: 400;
    }
    header .signin {
        text-align: right;
    }
    header .signin a {
        color: #ddd;
        margin-left: 20px;
    }
    .signin a:hover {
        border-bottom: solid 1px #ddd;
        display: inline;
        padding-bottom: 3px;
        cursor: pointer;
    }
    header .logo {
        font-size: 1.2rem;
    }
`;

const StyledFooter = styled.div`
    display: flex;
    border-top: 1px solid #ddd;
    padding: 6px 0px 12px 0px;
    font-size: .8rem;
    color: #666;
    flex-direction: row;

    .copyright, .contact {
        flex: 1;
    }
    .contact {
        text-align: right;
    }
    .contact a {
        margin-left: 20px;
    }
`;

const Footer = () => (
    <StyledFooter>
        <div className="copyright">
            &copy; {new Date().getFullYear()} Thong Nguyen
        </div>
        <div className="contact">
            <a href="https://github.com/ikumen/bits"><i className="icon-github-circled" title="projects"></i></a>
            <a href="https://github.com/ikumen/bits/issues">Contact</a>
            <Link to={{pathname: '/about'}}>About</Link>
        </div>
    </StyledFooter>
)

class Header extends React.Component {
    constructor(props) {
        super(props);
        this.onCurrentUserLoaded = this.onCurrentUserLoaded.bind(this);
        this.createNewBit = this.createNewBit.bind(this);
        this.onCreateNewBit = this.onCreateNewBit.bind(this);

        this.state = {
            user: false
        }
    }

    componentDidMount() {
        Log.info('Header.componentDidMount():')
        UserService.getCurrentUser()
            .then(this.onCurrentUserLoaded)
            .catch(err => Log.error(err));
    }

    onCurrentUserLoaded(user) {
        if (user) {
            this.setState({user: user});
        }
    }

    createNewBit(evt) {
        if (this.state.user) {
            BitService.create(this.state.user.id)
                .then(this.onCreateNewBit)
                .catch(err => Log.error(err));
        } else {
            //TODO: signout
        }
    }

    onCreateNewBit(bit) {
        Log.debug('Created bit:', bit);
        const url = '/@' + this.state.user.id + '/bits/' + bit.id;
        this.props.history.push(url);
    }

    render() {
        return <StyledHeader>
        <header>
            <div className="logo">
                <Link to={{pathname: this.state.user ? '/@' + this.state.user.id : '/'}}>
                    <i className="icon-spinner"></i> Bits
                </Link>
            </div>
            {this.state.user ?
                <div className="signin">
                    <a onClick={this.createNewBit}>New Bit</a>
                    <a href="/signout">Sign out</a> 
                </div>
            :   <div className="signin">
                    <a href="/signin">Sign in</a>
                </div>
            }
        </header>
        </StyledHeader>        
    }
}

export {Footer, Header, SubHeader, Page};