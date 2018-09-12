import React from 'react';
import ReactDOM from 'react-dom';
import BitService from '../../services/bits';
import {Link} from 'react-router-dom';
import styled from 'styled-components';

const BitList = styled.ul`
`;

const Bit = styled.li`
`;


class BitPage extends React.Component {
    constructor(props) {
        super(props);
        this.toggleEditMode = this.toggleEditMode.bind(this);
        this.setEditFocus = this.setEditFocus.bind(this);
        this.handleUnload = this.handleUnload.bind(this);
        this.cancelEditMode = this.cancelEditMode.bind(this);

        this.state = {
            userId: props.match.params.userId,
            bitId: props.match.params.bitId,
            isEditMode: false,
        }
    }

    cancelEditMode(evt) {
        console.log(evt.keyCode)
        if (evt.keyCode == 27) {
            this.setState({isEditMode: false});
            console.log('in cancel edit')
        }
    }

    saveDraft() {
        BitService.saveDraft(bit, {
            userId: this.state.userId,
            bitId: this.state.bitId,
            title: ReactDOM.findDOMNode(this.refs.description).textContent,
            content: ReactDOM.findDOMNode(this.refs.content).textContent
        })
    }

    handleUnload() {
        console.log('old description: ', this.state.bit.description)
        console.log('new description: ', ReactDOM.findDOMNode(this.refs.description).textContent);
    }

    componentDidMount() {
        BitService.get(this.state.userId, this.state.bitId)
            .then(bit => this.setState({bit: bit}))
            .catch(err => console.log(err));
        this.setEditFocus();
        window.addEventListener('beforeunload', this.handleUnload);
        document.addEventListener('keydown', this.cancelEditMode);
    }

    componentDidUpdate() {
        this.setEditFocus();
    }

    componentWillUnmount() {
        window.removeEventListener('beforeunload', this.handleUnload);
        document.removeEventListener('keydown', this.cancelEditMode);
        this.handleUnload();
    }

    setEditFocus() {
        if (this.state.isEditMode) {
            ReactDOM.findDOMNode(this.refs.description).focus();
        }
    }

    toggleEditMode() {
        this.setState({isEditMode: !this.state.isEditMode})
        this.setEditFocus();
    }

    render() {
        const bit = this.state.bit;
        return <div>
            {this.state.bit && 
            <div>
                <button onClick={this.toggleEditMode}>{this.state.isEditMode ? 'Preview' : 'Edit'}</button>
                <h1 suppressContentEditableWarning={true} ref="description"
                        contentEditable={this.state.isEditMode}>
                    {bit.description}
                </h1>             
                <div suppressContentEditableWarning={true} 
                        contentEditable={this.state.isEditMode}>
                    {bit.content}
                </div>
            </div>
            }
        </div>
    }
}


class BitIndexPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            userId: (props.match.params.userId || '') // TODO: should error if no user
        }
    }

    componentDidMount() {
        BitService.list(this.state.userId)
            .then(bits => {
                this.setState({bits: bits.map((bit, i) => {
                    return <Bit key={i}>
                        <Link to={{
                            pathname: "/@" + this.state.userId + '/bits/' + bit._id,
                        }}>{bit.description}
                        </Link>
                    </Bit>
                })});
            })
            .catch(err => console.log(err));
    }

    render() {
        return <BitList>
            {this.state.bits}
        </BitList>
    }
 }

export {BitPage, BitIndexPage};