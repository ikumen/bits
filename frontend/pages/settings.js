import React from 'react';
import { Link } from 'react-router-dom';
import { Page } from '../components';
import { BitService } from '../services';

class SettingsPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.reload = this.reload.bind(this);
  }

  componentDidMount() {
    BitService.settings()
      .then(settings => this.setState({settings}))
  }

  reload() {
    BitService.reload()
      .then(settings => this.setState({settings}));
  }

  render() {
    const {settings} = this.state;
    return <Page>
      <h2 className="f2 dark-gray">Settings</h2>
      <ul className="list w-100 pa0 ma0 mb2">
        <li className="flex items-center lh-copy ph0 pv3 bb b--black-10">
          <div className="flex-auto v-top">
            <div>Loads all bits from GitHub to our local db.</div>
            <div className="f6 gray i">Last loaded at: {settings && settings.loaded_at}</div>
          </div>
          <div className="v-top">
            <button onClick={this.reload} className="f6 ph3 pv2 bw0 dib white bg-blue">Reload Bits</button>
          </div>
        </li>
      </ul>
    </Page>
  }
}

export default SettingsPage;
