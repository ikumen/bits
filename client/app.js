/**
 * Entry point for frontend application. Mostly setup, boilerplate and 
 * services.
 */
import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route} from 'react-router-dom';
import AboutPage from './containers/about';
import {BitIndexPage, BitPage} from './containers/bits';
import {Footer, Header} from './components/layouts';

const App = () => (
    <BrowserRouter>
        <div className="container">
            <Route exact={true} path="/" component={AboutPage} />
            <Route exact={true} path="/about" component={AboutPage} />
            <Route path={`/@:userId/bits/:bitId`} component={BitPage} />
            <Route exact path={`/@:userId`} component={BitIndexPage} />
        </div>
    </BrowserRouter>
);

ReactDOM.render(<Header />, document.getElementById('header'));
ReactDOM.render(<App />, document.getElementById('app'));
ReactDOM.render(<Footer />, document.getElementById('footer'));
