/**
 * Entry point for frontend application. Mostly setup, boilerplate and 
 * services.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route} from 'react-router-dom';
import AboutPage from './containers/about';
import {BitIndexPage, BitPage} from './containers/bits';

const App = () => (
    <BrowserRouter>
        <div>
            <Route exact={true} path="/" component={AboutPage} />
            <Route path={`/u::userId/bits/:bitId`} component={BitPage} />
            <Route exact path={`/u::userId`} component={BitIndexPage} />
        </div>
    </BrowserRouter>
);

ReactDOM.render(<App />, document.getElementById('app'));