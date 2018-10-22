/**
 * Entry point for frontend application. Mostly setup, boilerplate and 
 * services.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route, Switch} from 'react-router-dom';
import AboutPage from './containers/about';
import UserPage from './containers/user';
import {BitPage} from './containers/bit';
import {Footer, Header, Page} from './components/layouts';
import UserService from './services/user';
import styled from 'styled-components';


const AppWrapper = styled.div`
    min-height: 100vh;
    display: flex;
    flex-direction: column;
`;

function withAuthUser(Cpnt, props) {
    return <Cpnt {...props} />
}

const ErrorPage = (props) => {
    const error = props.getAndClearError();
    return <Page>{error ? JSON.stringify(error): <h3>Doh, we couldn't what you're looking for!</h3>}</Page>
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.handleError = this.handleError.bind(this);
        this.getAndClearError = this.getAndClearError.bind(this);
        this.onHistoryChange = this.onHistoryChange.bind(this);
        this.state = {};
        this.clearError();
    }

    componentDidMount() {
        UserService.getCurrentUser()
            .then(authUser => this.setState({authUser: authUser}))
    }

    onHistoryChange(url, replace=false) {
        replace === true ? this.props.history.replace(url) : 
            this.props.history.push(url);
    }

    handleError(error) {
        this.hasError = true;
        this.error = error;
        this.onHistoryChange('/error', true);
    }

    clearError() {
        this.hasError = false;
        this.error = undefined;
    }

    getAndClearError() {
        const error = this.error;
        this.clearError();
        return error;
    }

    render() {
        const {authUser} = this.state
            , getAndClearError = this.getAndClearError
            , handleError = this.handleError;

        return <React.Fragment>
            <Header authUser={authUser} handleError={handleError} onHistoryChange={this.onHistoryChange} />
            <Switch>
                <Route exact={true} path="/" render={(props) => withAuthUser(AboutPage, {...props, authUser, handleError})} />
                <Route exact={true} path="/about" render={(props) => withAuthUser(AboutPage, {...props, authUser, handleError})} />
                <Route exact path={`/@:atUserId`} render={(props) => withAuthUser(UserPage, {...props, authUser, handleError})} />
                <Route path={`/@:atUserId/bits/:bitId/:edit?`} render={(props) => withAuthUser(BitPage, {...props, authUser, handleError})} />
                <Route render={(props) => <ErrorPage {...{...props, getAndClearError}} />} />
            </Switch>
            <Footer authUser={authUser} />
        </React.Fragment>
    }
}



ReactDOM.render(
<AppWrapper>
    <BrowserRouter>
        <Route path="*" component={App} />
    </BrowserRouter>
</AppWrapper>, 
document.getElementById('app'));
