import React from 'react';
import { Link } from 'react-router-dom';
import { Page } from '../components';
import { UserService } from '../services';

class SettingsPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {bits: {total: 0, published: 0}};
    this.reload = this.reload.bind(this);
  }

  componentDidMount() {
    UserService.stats()
      .then(stats => {
        const {bits, syncs} = stats;        
        syncs.forEach(s => this.setState({[s.id+'ed_at']: s.synced_at}));
        this.setState({
          bits: {
            total: bits.length,
            published: (bits.filter(b => b.published_at)).length
        }});
    });
  }

  reload() {
    UserService.reload()
      .then(s => this.setState({[s.id+'ed_at']: s.synced_at}))
  }

  render() {
    const {bits, downloaded_at, uploaded_at} = this.state;
    return <Page>
      <h2 className="f2 dark-gray">Settings</h2>
      <ul className="list w-100 pa0 ma0 mb2">
        <li className="flex items-center lh-copy ph0 pv3 bt b--black-10">
          <div className="flex v-top w-100">
            <div className="f3 w-50">{bits.total} total</div>
            <div className="f3 w-50">{bits.published} published</div>
          </div>
        </li>

        <li className="flex items-center lh-copy ph0 pv3 bt b--black-10">
          <div className="flex-auto v-top">
            <div>Download all bits from GitHub to our local db.</div>
            <div className="f6 gray i">Last downloaded at: {downloaded_at || ''}</div>
          </div>
          <div className="v-top">
            <button onClick={this.reload} className="f6 ph3 pv2 bw0 dib white bg-red">Download Bits</button>
          </div>
        </li>

        <li className="flex items-center lh-copy ph0 pv3 bt b--black-10">
          <div className="flex-auto v-top">
            <div>Upload all local bits to GitHub.</div>
            <div className="f6 gray i">Last uploaded at: {uploaded_at || ''}</div>
          </div>
          <div className="v-top">
            <button onClick={this.reload} className="f6 ph3 pv2 bw0 dib white bg-blue">Upload Bits</button>
          </div>
        </li>
      </ul>
    </Page>
  }
}

export default SettingsPage;
