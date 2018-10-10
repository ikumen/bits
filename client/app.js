/**
 * Entry point for frontend application. Mostly setup, boilerplate and 
 * services.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route} from 'react-router-dom';
import AboutPage from './containers/about';
import UserPage from './containers/user';
import {BitPage} from './containers/bit';
import {Footer, Header} from './components/layouts';
import styled from 'styled-components';


const AppWrapper = styled.div`
    min-height: 100vh;
    display: flex;
    flex-direction: column;
`;
const App = () => (
    <BrowserRouter>
        <AppWrapper>
            <Route path="*" component={Header} />
            <Route exact={true} path="/" component={AboutPage} />
            <Route exact={true} path="/about" component={AboutPage} />
            <Route exact path={`/@:atUserId`} component={UserPage} />
            <Route path={`/@:atUserId/bits/:bitId/:edit?`} component={BitPage} />
            <Route path="*" component={Footer} />
        </AppWrapper>  
    </BrowserRouter>
);

ReactDOM.render(<App />, document.getElementById('app'));
