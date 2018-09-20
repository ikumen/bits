import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Log from '../../services/logger';
import {Page, SubHeader} from '../../components/layouts';
import UserProfile from '../../components/userprofile';


const BitList = styled.ul`
    padding: 0;
    margin-top: 20px;
`;

const Bit = styled.li`
`;

class UserPage extends React.Component {
    constructor(props) {
        super(props);

        this.onBitsLoaded = this.onBitsLoaded.bind(this);
        this.onAtUserLoaded = this.onAtUserLoaded.bind(this);

        //TODO: check for userId

        this.state = {
            atUserId: props.match.params.userId,
        }

    }

    componentDidMount() {
        UserService.getAtUser(this.state.atUserId)
            .then(this.onAtUserLoaded)
            .catch(err => Log.error(err));

        BitService.list(this.state.atUserId)
            .then(this.onBitsLoaded)
            .catch(err => Log.error(err));
    }

    onBitsLoaded(bits) {
        this.setState({bits: bits.map((bit, i) => {
            return <Bit key={i}>
                <Link to={{pathname: '/@' + this.state.atUserId + '/bits/' + bit._id}}>
                    {bit.description || bit._id}
                </Link>
            </Bit>
        })});
    }

    onAtUserLoaded(user) {
        this.setState({
            atUser: user,
            atUserProfile: <UserProfile user={user} />
        });
    }

    render() {
        return <Page>
            <SubHeader>
                {this.state.atUserProfile}
            </SubHeader>
            <BitList>
                {this.state.bits}
            </BitList>
        </Page>

    }
 }

export default UserPage;