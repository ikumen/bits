import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Log from '../../services/logger';
import Utils from '../../services/utils';
import {Page, SubHeader} from '../../components/layouts';
import UserProfile from '../../components/userprofile';


const StyledBitList = styled.ul`
    padding: 0;
    margin-top: 20px;
`;

const Bit = styled.li`
    margin-bottom: 4px;
    display: flex;
    flex-direction: row;

    & .title {
        flex: 1;
        display: flex;
        flex-direction: column;
        margin-left: 4px;
    }

    & a, & .tags {
        flex: 1;
    }
    .tags {
        margin-top: -6px;
        color: #aaa;
        font-size: .9rem;
    }

`;

const StyledDate = styled.span`
    font-size: .9rem;
    font-family: 'Courier New';
    color: #aaa;
    margin-top: 2px;
    margin-right: 2px;
`;


const BitList = ({user, bits}) => {
    const options = {year: 'numeric', month: 'short'}
    return <StyledBitList> 
        {bits && bits.map((bit) => 
            <Bit key={bit.id}>
                {bit.published_at ? 
                    <StyledDate>{Utils.formatDateString(bit.published_at)} &raquo; </StyledDate>
                    :
                    <StyledDate>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Draft &raquo; </StyledDate>
                }
                <div className="title">
                    <Link to={{pathname: '/@' + user.id + '/bits/' + bit.id}}>
                        {bit.title || 'New Bit '}
                    </Link>
                    <div className="tags">
                        {bit.tags.join(', ')}
                    </div>
                </div>
                <div>
                </div>
            </Bit>
        )}
    </StyledBitList>
};

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