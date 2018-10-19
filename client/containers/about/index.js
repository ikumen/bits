import React from 'react';
import {Page} from '../../components/layouts';

const AboutPage = (props) => {
    return <Page className="about">
        <h1>Welcome to Bits</h1>
        <div>
        <p>
            Bits is my no frills <a href="https://gist.github.com/">Gist</a> powered 
            blog. It's an <a href="https://github.com/ikumen/bits">ongoing project</a> that 
            I use to learn Python and React. You're welcome to give it a try or <a href="https://github.com/ikumen/bits">fork it</a> for yourself. 
        </p>
        <p>
        It has the following features:
        </p>
        <ul>
            <li>distraction free, simple plain text editor with support for markdown</li>
            <li>for introverts, no social media baggage</li>
            <li><a href="https://en.wikipedia.org/wiki/All_your_base_are_belong_to_us">all 
                your bits belong to us</a>, just kidding, the Gist are under your account
            </li>
        </ul>
        </div>
        {props.authUser && <div hidden={props.authUser}>
        <p>
            To get started, all you need is a <a href="https://github.com">GitHub</a> account 
            and a little <a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet">knowledge of Markdown</a>. 
        </p>
        <p>
            Sign in when you're ready.
        </p>
        </div>}
    </Page>
};

export default AboutPage;