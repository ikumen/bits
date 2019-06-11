import React from 'react';
import { Link } from 'react-router-dom';

import { Page } from '../components';

const AboutPage = () => (
  <Page>
    <h1 className="f3 cf f2-ns dark-gray">About</h1>
    <p className="f4">
    Thanks for checking out <Link to="/">bits</Link>&mdash;my no frills, <a href="//gist.github.com">gist</a> backed, <a href="//cloud.google.com/appengine/">App Engine</a> powered micro blog. 
    It's an ongoing <a href="//github.com/ikumen/bits">project</a> I use to learn <a href="//flask.pocoo.org/">Flask</a> and <a href="//reactjs.org">React</a>. 
    </p>
    <p className="f4">
    
    </p>
  </Page>
);

export default AboutPage;
