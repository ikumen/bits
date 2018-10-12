import React from 'react';
import styled from 'styled-components';
import Utils from '../../services/utils';
import Log from '../../services/logger';
import {markedWithHljs} from '../../services/renderers';

const Editor = styled.div`
    padding: 0;
    margin: 30px 0;
    & .wrapper > .edit, & .wrapper > .view{
        padding: 0px 6px;
    }
    #title.edit, #content.edit, #pubdate.edit, #tags.edit {
        outline: none;
        opacity: 1;
        //background: #F8F4E3;
        background: #fff;
    }
    #content pre {
        background: #2b303b;
        padding: 10px;
        font-size: .8rem;
        font-weight: 100;
        color: #c0c5ce;
        overflow: auto;
        word-wrap: normal;
        white-space: pre;
    }
    & #title {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    & [contenteditable=true]:empty:before {
        content: attr(placeholder);
        opacity: .2;
        display: block; /* For Firefox */
    }
    & .meta {
        margin: 0px 0 40px;
        width: 100%;
        display: flex;
        flex-flow: flex-start;
        font-size: .9rem;
    }
    & #pubdate {
        margin-right: 30px;
        white-space:nowrap;
    }
    & .meta .view, & .meta i  {
        color: #bbb;
    }
`;

class Editable extends React.Component {
    constructor(props) {
        super(props);
        this.onInput = this.onInput.bind(this);
        this.setValue = this.setValue.bind(this);
        this.elementRef = React.createRef();
        this.state = {hasErrors: false}
    }

    componentDidMount() {
        this.setValue(this.props);
    }

    componentDidUpdate(prevProps) {
        Log.info('prev=', prevProps, ', props=', this.props)
        if (!this.state.hasErrors)
            this.setValue(this.props)
    }

    /* 
     * Decide if we should re-render this component.
     * 
     * DO re-render under the following conditions:
     *  - if value is 'undefined', meaning we just loaded for the first time
     *  - if current value and next value is equal, meaning we are not editing this component
     *  - if parent bit id has not changed, meaning we are still on same bit
     *  - if don't have any errors, details below:
     *    - when there are errors, the value is not pushed to parent update method 
     *      to prevent errors from being auto-saved. So if parent doesn't have our
     *      latest changes (w/ the errors), we should have it push back down a new
     *      value to re-render, which would wipe away our current edit
     */
    shouldComponentUpdate(nextProps, nextState) {
        const {value, isEqual, bitId} = this.props;
        const areEqual = isEqual ? isEqual(value, nextProps.value) : value === nextProps.value;
        return (value === undefined || areEqual || bitId != nextProps.bitId) && !this.state.hasErrors;
    }

    setValue({value, editable, viewRenderer, editRenderer}) {
        if (value === undefined) { return; }
        if (editable) { this.elementRef.current.innerText = editRenderer ? editRenderer(value) : value; } 
        else { 
            this.elementRef.current.innerHTML = viewRenderer ? viewRenderer(value) : value; 
        }
    }

    onInput(e) {
        const {validator, preprocessor, onUpdate} = this.props;
        const value = e.target.innerText;
        if (!validator || validator(value)) {
            this.setState({hasErrors: false})
            onUpdate(this.props.id, (preprocessor ? preprocessor(value) : value));
        } else {
            Log.info('Invalid input!')
            this.setState({hasErrors: true})
        }
    }

    render() {
        const {id, editable, placeholder} = this.props;
        return <div id={id}
            className={editable ? 'edit' : 'view'}
            contentEditable={editable}
            placeholder={placeholder}
            onInput={this.onInput}
            ref={this.elementRef}>
        </div>
    }
}

const Title = (props) => (
    <Editable id="title" {...props} placeholder="Enter a title" />
);

const Pubdate = ({value, ...props}) => (
    <React.Fragment>
        <i className="icon-calendar"></i>&nbsp;
        <Editable id="pubdate" {...{...props, value: value ? Utils.toSimpleISOFormat(value) : value}} 
            placeholder="e.g, YYYY-MM-DD"/>
    </React.Fragment>
);

/*
isEqual={Utils.arraysAreEqual}
viewRenderer={Utils.flattenArray}
editRenderer={Utils.flattenArray} */
const Tags = (props) => (
    <React.Fragment>
        <i className="icon-tags"></i>&nbsp;
        <Editable id="tags" {...props} placeholder="e.g, java, spring-jpa (comma separated, 3 max)"/>
    </React.Fragment>
);

const Content = (props) => (
    <Editable id="content" {...props}
            viewRenderer={markedWithHljs}
            placeholder="e.g, Enter your markdown"/>
);


export {Title, Content, Pubdate, Tags, Editable, Editor};