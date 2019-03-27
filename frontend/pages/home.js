import React from 'react';
import { Link } from 'react-router-dom';

import { Page } from '../components';
import { BitService } from '../services';


class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {}
  }

  componentDidMount() {
    BitService.all()
      .then(bits => this.setState({ bits}));
  }


  
  render() {
    const { bits } = this.state;
    return <Page>
      <ul className="list w-100 pv3 ph0 border-box">
        { bits && bits.map((bit) => {
          return <li key={bit.id} className="mb4">
            <h2 className="f3 fw6 mb1">
              <Link to={`/bits/${bit.id}`} className="link dim mid-gray">{bit.description || 'Untitled'}</Link>
            </h2>
            <p className="f5 mt0 lh-copy">
              {bit.content ? bit.content.substr(0, 300) : ''}... 
              &nbsp;<Link to={`/bits/${bit.id}`} className="link dim green">Read &rarr;</Link>
            </p>
          </li>
        })}
      </ul>
    </Page>
  }
}

export default HomePage;
  