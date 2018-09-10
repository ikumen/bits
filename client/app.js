/**
 * Entry point for frontend application. Mostly setup, boilerplate and 
 * services.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route, Link} from 'react-router-dom';
import AboutPage from './containers/about';
import UserPage from './containers/user';

const App = () => (
    <BrowserRouter>
        <div>
            <Route exact path="/" component={AboutPage} />
            <Route path={`/u::slug`} component={UserPage} />
        </div>
    </BrowserRouter>
);

ReactDOM.render(<App />, document.getElementById('app'));