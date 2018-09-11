import React from 'react';

class AboutPage extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div>
            Welcome to bits!
            <a href="/signin">Signin with Github</a>
        </div>
    }
}

export default AboutPage;