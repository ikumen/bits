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
            <Bit key={bit._id}>
                <Link to={{pathname: '/@' + user._id + '/bits/' + bit._id}}>
                    {bit.description || bit._id}
                </Link>
            </Bit>
        )}
    </StyledBitList>
);

class UserPage extends React.Component {
    constructor(props) {
        super(props);

        this.onBitsLoaded = this.onBitsLoaded.bind(this);

        //TODO: check for userId
        this.state = {
            atUserId: props.match.params.userId,
        }
    }

    componentDidMount() {
        BitService.list(this.state.atUserId)
            .then(this.onBitsLoaded)
            .catch(err => Log.error(err));
    }

    onBitsLoaded(resp) {
        const {bits, ...user} = resp
        this.setState({atUser: user, bits: bits});
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