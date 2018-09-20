import React from 'react';
import styled from 'styled-components';

const Profile = styled.div`
    flex: 1;
    display: flex;
    align-items: center;

    img {
        margin-right: 10px;
    }
`;

const UserProfile = (props) => (
    <Profile>
        <img src={props.user.avatar_url} width='40'/> <a href={'/@' + props.user._id}>{props.user._id}</a>
    </Profile>
);

export default UserProfile;
