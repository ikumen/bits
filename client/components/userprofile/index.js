import React from 'react';
import {Link} from 'react-router-dom';
import styled from 'styled-components';

const StyledProfile = styled.div`
    flex: 1;
    display: flex;
    align-items: center;

    img {
        margin-right: 10px;
    }
`;

const UserProfile = ({atUser}) => (
    <StyledProfile>
        {atUser && <div>
            <img src={atUser.avatar_url} width='40'/> 
            <Link to={{pathname: '/@' + atUser._id}}>
                {atUser.name ? atUser.name : atUser._id}
            </Link>
        </div>}
    </StyledProfile>
);

export default UserProfile;
