import React from 'react';
import {Link} from 'react-router-dom';
import styled from 'styled-components';

const StyledProfile = styled.div`
    flex: 1;
    display: flex;
    align-items: center;
    font-size: 1.1rem;
    img {
        width: 40px;
        margin-right: 10px;
    }
    .links {
        display: flex;
        align-items: center;
        flex-direction: row;
        flex-wrap: wrap;
    }
    .user-link {
        font-size: 1.1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .gh-links {
        font-size: .9rem;
        opacity: .6;        
    }
`;


const UserProfile = ({atUser={}, isAuthUser, bit}) => {
    const baseGistUrl = 'https://gist.github.com/';
    const url = baseGistUrl + (bit ? (atUser.id + '/' + bit.id) : ('search?q=user%3A' + atUser.id + '+filename%3Abit.md'));
    return <StyledProfile>
        {atUser && <React.Fragment>
            <img src={atUser.avatar_url}/>
            <div className="links">
                <Link className="user-link" to={{pathname: '/@' + atUser.id}}>{atUser.name ? atUser.name : atUser.id}</Link>&nbsp;
                {isAuthUser && 
                <div className="gh-links"><small>(</small><a href={url} target="_new"><i className="icon-github-circled"></i>Gist</a><small>)</small></div>
                }
            </div>
        </React.Fragment>}
    </StyledProfile>
};

export default UserProfile;
