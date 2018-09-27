import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Log from '../../services/logger';
import {Page, SubHeader} from '../../components/layouts';
import UserProfile from '../../components/userprofile';


const StyledBitList = styled.ul`
    padding: 0;
    margin-top: 20px;
`;

const Bit = styled.li`
`;

const BitList = ({user, bits}) => (
    <StyledBitList> 
        {bits && bits.map((bit) => 
            <Bit key={bit.id}>
                <Link to={{pathname: '/@' + user.id + '/bits/' + bit.id}}>
                    {bit.title || 'New Bit (' + bit.created_at + ')'}
                </Link>
            </Bit>
        )}
    </StyledBitList>
);

class UserPage extends React.Component {
    constructor(props) {
        super(props);
        //TODO: check for userId
        this.state = {
            atUserId: props.match.params.atUserId,
        }
    }

    componentDidMount() {
        Promise.all([
                UserService.getAtUser(this.state.atUserId),
                BitService.list(this.state.atUserId)])
            .then(([atUser, bits]) => this.setState({atUser: atUser, bits: bits}))
            .catch(err => Log.error(err));
    }

    render() {
        return <Page>
            <SubHeader>
                <UserProfile atUser={this.state.atUser} />
            </SubHeader>
            <BitList user={this.state.atUser} bits={this.state.bits} />
        </Page>

    }
 }

export default UserPage;