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
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
`;
const Meta = styled.div`
    margin-top: -2px;
    display: flex;
    flex-direction: row;
    font-size: .9rem;
    opacity: .4;
    & time {
        margin-right: 10px;
    }
    & i {
        opacity: .3;
    }
`;

const PublishDate = ({pubdate}) => {
    const formattedDate = pubdate ? Utils.toSimpleISOFormat(pubdate) : 'Draft';
    return <time dateTime={formattedDate}><i className="icon-calendar"></i> {formattedDate}</time>
};

const TagList = ({tags}) => {
    return tags && tags.length > 0 ? <div><i className="icon-tags"></i> {tags.join(', ')}</div> : <div></div>
        
}

const BitList = ({user, bits}) => {
    const options = {year: 'numeric', month: 'short'}
    return <StyledBitList> 
        {bits && bits.map((bit) => 
            <Bit key={bit.id}>
                <Link className="link" to={{pathname: '/@' + user.id + '/bits/' + bit.id}}>
                    {bit.title || 'New Bit '}
                </Link>
                <Meta>
                    <PublishDate pubdate={bit.pubdate} />
                    <TagList tags={bit.tags} />
                </Meta>
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