import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Switch, Route, Link } from 'react-router-dom';

import HomePage from './pages/home';
import BitPage from './pages/bit';
import AboutPage from './pages/about';
import ErrorPage from './pages/errors';
import SettingsPage from './pages/settings';
import Search from './search';
import { UserService, getDateParts } from './services';


class Header extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      search: false
    }
  }

  render() {
    const { user={} } = this.props;
    return <nav className="flex w-100 border-box pv1 ph3 ph5-m ph6-ns bg-white">
      <h1 className="f2 f1-ns fw6 v-mid dark-gray dim w-20 pointer" onClick={()=> this.props.changeRoute('/')} title="Home">bits</h1>
      <div className="flex justify-end items-center w-80 tr">
        {/* <i className="f3 f2-ns material-icons dim lighter-gray pointer" 
            onClick={()=> this.setState({search: true})}
          >search
        </i> */}
        {/* <Search /> */}
      { user.authenticated && 
        <Link className="link dim gray dib" to="/bits/new/edit">
          <i className="f2 f1-ns material-icons dim green ml3">playlist_add</i>
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
  return <footer className="dt cf w-100 border-box b--light-gray pa3 ph5-m ph6-ns bt pb5 f6 f5-ns gray">
    <div className="dtc tl lighter-gray">
      &copy; <span className="dn dib-ns">{year}</span> Thong Nguyen
    </div>
    <div className="dtc tr">
      <Link to="/about" className="link dim gray mr1 mr3-ns">About</Link>
      {(user && user.authenticated) && <Link to="/settings" className="link dim gray mr1 mr3-ns">Settings</Link>}
      <SignInOutLink authenticated={user && user.authenticated}/>
    </div>
  </footer>
};

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.changeRoute = this.changeRoute.bind(this);
  }

  componentDidMount() {
    UserService.getCurrentUser()
      .then(user => this.setState({user}));
  }

  changeRoute(location, replace=false) {
    const pathname = typeof location === 'string' ? location : location.pathname;
    if (pathname !== this.props.location.pathname) {
      replace === true ? this.props.history.replace(location) :
        this.props.history.push(location);
    }
  }

  render() {
    const user = this.state.user || {};
    return <React.Fragment>
      <Header user={user} changeRoute={this.changeRoute} />
      <Switch>
        <Route exact={true} path="/" render={(props) => <HomePage {...props} changeRoute={this.changeRoute} /> }/>
        <Route path={`/bits/:id/:edit?`} render={(props) => <BitPage {...props} user={user} /> }/>
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
