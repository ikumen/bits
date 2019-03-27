import React from 'react';
import { Link } from 'react-router-dom';

import { Page } from '../components';

const ErrorPage = (props) => {
  const { code  } = props.match.params;
  return <Page>
    {(() => {
      switch(code) {
        case '404': return <h2>Doh, we can't seem to find what you're looking for!</h2>;
        case '403': return <h2>Uh-oh, you're not authorized to do that. Try <Link to="/signin" className="link dim">signing in</Link> first.</h2>;
        default: return <h2>Oh noes, this doesn't look good! Looks like we're having 
          some technical issues, please try again later</h2>;
      }
    })()}
  </Page>
};

export default ErrorPage;
