import React from 'react';
import { Link } from 'react-router-dom';

import { Page } from '../components';
import { BitService } from '../services';


class HomePage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {}
    this.onBitsLoaded = this.onBitsLoaded.bind(this);
    this.changeRoute = this.changeRoute.bind(this);
  }

  componentDidMount() {
    this.loadBits();
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.location.hash !== prevProps.location.hash) {
      this.loadBits();
    }
  }

  loadBits() {
    const { hash } = this.props.location;
    if (hash === '#drafts') {
      BitService.allDrafts().then(this.onBitsLoaded); 
    } else if (hash === '#published') {
      BitService.allPublished().then(this.onBitsLoaded);
    } else {
      BitService.all().then(this.onBitsLoaded);
    }
  }

  onBitsLoaded(bits) {
    this.setState({bits});
    this.scrollToOffsetsIfNeeded(this.props);
  }

  scrollToOffsetsIfNeeded(props) {
    const {xOffset, yOffset} = props.location.state || {};
    if (typeof xOffset !== 'undefined' && typeof yOffset !== 'undefined') {
      this.setLocationState(props, {});
      window.scrollTo(xOffset, yOffset);
    }
  }

  setLocationState(props, state) {
    props.history.replace('', state);
  }

  changeRoute(id) {
    this.setLocationState(this.props, {xOffset: window.pageXOffset, yOffset: window.pageYOffset});
    this.props.history.push(`/bits/${id}`);
  }

  render() {
    const { bits } = this.state;
    return <Page>
      <div className="fr cf flex">
        <Link className="mh2 link" to="">all</Link>
        <Link className="mh2 link" to="#drafts">drafts</Link>
        <Link className="mh2 link" to="#published">published</Link>
      </div>
      <ul className="list w-100 pv3 ph0 dark-gray border-box">
        { bits && bits.map((bit) => {
          return <li key={bit.id} className="mb5">
            <h2 className="f3 fw5 mb2 link dim pointer" onClick={() => this.changeRoute(bit.id)}>
              {bit.description || 'Untitled'}
            </h2>
            <p className="f4 f4-ns mt0 lh-copy">
              {bit.teaser ? bit.teaser + '...' : ''}
              &nbsp; <Link to={`/bits/${bit.id}`} className="link dim green">Read &rarr;</Link>
            </p>
          </li>
        })}
      </ul>
    </Page>
  }
}

export default HomePage;
  