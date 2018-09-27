import React from 'react';
import {Link} from 'react-router-dom';
import styled from 'styled-components';

const StyledProfile = styled.div`
    flex: 1;
    display: flex;
    align-items: center;

    img {
        width: 40px;
        margin-right: 10px;
    }
`;

const UserProfile = ({atUser}) => (
    <StyledProfile>
        {atUser && <div>
            <img src={atUser.avatar_url}/> 
            <Link to={{pathname: '/@' + atUser.id}}>
                {atUser.name ? atUser.name : atUser.id}
            </Link>
        </div>}
    </StyledProfile>
);

export default UserProfile;
