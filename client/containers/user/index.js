import React from 'react';
import BitList from '../../components/bits';

class UserPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: (props.match.params.slug || ''),
            url: ((props.location.state || '').url || '')
        }
        console.log(this.state)
    }

    render() {
        return <div>
            <BitList user={this.state.user} />
        </div>;
    }
 }

export default UserPage;