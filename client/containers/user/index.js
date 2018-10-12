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
    flex-direction: row;
    align-items: baseline;
    //font-family: monospace;
    font-size: 1.1rem;
    flex-wrap: nowrap;
    time, .tags {
        font-family: monospace;
        font-size: .9rem;
        color: #bbb;
    }
    time {
        margin-right: 10px;
        white-space: nowrap;
    }
    .tags {
        margin-top: -4px;
    }
`;

const Pubdate = ({value}) => {
    if (value) {
        const formattedDate = Utils.toSimpleISOFormat(value);    
        return <time dateTime={formattedDate}>{formattedDate}</time>
    } else {
        return <time>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Draft</time>
    }
};

const Tags = ({value}) => {
    return value && value.length > 0 ? <div className="tags">[{value.join(', ')}]</div> : <div></div>
        
}


const BitList = ({user, bits}) => {
    return bits ? 
        <StyledBitList> {bits.map((bit) => {
            const {id, title='New Bit', pubdate, tags, created_at} = bit;
            const formattedDate = pubdate ? Utils.toSimpleISOFormat(pubdate) : '';
            return <Bit key={id}>
                <Pubdate value={pubdate} />
                <div className="title-tags">
                    {pubdate ? 
                        <Link to={{pathname: '/@' + user.id + '/bits/' + bit.id}}>
                            {bit.title || ''}
                        </Link>
                    :   <React.Fragment>
                        <Link to={{pathname: '/@' + user.id + '/bits/' + bit.id + '/edit'}}>
                            {bit.title || 'No title'}
                        </Link>
                        </React.Fragment>
                    } 
                    <Tags className="tags" value={bit.tags} />
                </div>
            </Bit>})}
        </StyledBitList> 
        : <div></div>
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