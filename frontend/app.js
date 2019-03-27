import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Switch, Route, Link } from 'react-router-dom';

import HomePage from './pages/home';
import BitPage from './pages/bit';
import AboutPage from './pages/about';
import ErrorPage from './pages/errors';
import SettingsPage from './pages/settings';
import { UserService, getDateParts } from './services'


class Header extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    const { user={} } = this.props;
    return <nav className="dt w-100 border-box pv1 ph3 ph5-m ph6-ns bg-white">
      <Link className="dtc v-mid dark-gray link dim w-20" to="/" title="Home">
        <h1 className="f4 fw6 f1-ns">bits</h1>
      </Link>
      <div className="dtc v-mid w-80 tr dn-">
        <a href="">
           <i className="material-icons dim lighter-gray v-btm md-36">search</i>
        </a>
      { user.authenticated && 
        <Link className="link dim gray dib" to="/bits/new/edit">
          <i className="material-icons dim green ml3 md-36">playlist_add</i>
        </Link> }
      </div>
    </nav>
  }
}


const SignInOutLink = ({authenticated}) => {
  return <a 
      className="link dim gray dib" 
      href={authenticated ? '/signout' : '/signin'}>
      {authenticated ? 'Signout' : 'Signin'}
    </a>
};

const Footer = ({user = {}}) => {
  const {year} = getDateParts(new Date());
  return <footer className="dt cf w-100 border-box b--light-gray pa3 ph5-m ph6-ns bt f7 f6-ns gray">
    <div className="dtc tl f7 lighter-gray">
      &copy; {year} Thong Nguyen
    </div>
    <div className="dtc tr">
      <Link to="/about" className="link dim gray mr3">About</Link>
      {(user && user.authenticated) && <Link to="/settings" className="link dim gray mr3">Settings</Link>}
      <SignInOutLink authenticated={user && user.authenticated}/>
    </div>
  </footer>
};

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  componentDidMount() {
    UserService.getCurrentUser()
      .then(user => this.setState({user}));
  }

  changeRoute(path, replace=false) {
    replace === true ? this.props.history.replace(path) :
      this.props.history.push(path);
  }

  render() {
    const {user} = this.state;
    return <React.Fragment>
      {user && <Header user={user} />}
      <Switch>
        <Route exact={true} path="/" component={HomePage} />
        <Route path={`/bits/:id/:edit?`} render={(props) => <BitPage {...props} user={user} /> } />
        <Route path={`/errors/:code`} component={ErrorPage} />
        <Route exact={true} path="/about" component={AboutPage} />
        <Route exact={true} path="/settings" component={SettingsPage} />
      </Switch>
      <Footer user={user} />
    </React.Fragment>
  }
}

ReactDOM.render(
  <BrowserRouter>
    <Route path="*" component={App} />
  </BrowserRouter>,  
  document.getElementById('app')
)
