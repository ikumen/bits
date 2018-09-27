import React from 'react';
import BitService from '../../services/bits';
import marked from 'marked';
import Log from '../../services/logger';
import { SubHeader } from '../layouts';
import UserProfile from '../../components/userprofile';
import styled from 'styled-components';

const ActionBar = styled.div`
    flex: 1;
    display: flex;
    align-items: center;
    flex-direction: row-reverse;
`;

const Action = styled.button`
    font-size: .7rem;
    padding: 3px 12px;
    cursor: pointer;

    &.danger {
        background-color: red;
        color: #fff;
        opacity: .6;
    }
`;

const StyledEditor = styled.div`
    margin-bottom: 40px;
    padding: 0;
    margin: 0;
    &.editor .content, &.editor .title {
        outline: none;
        background: #F8F4E3;
    }
    &[contenteditable=true]:empty:before {
        content: attr(placeholder);
        display: block; /* For Firefox */
    }
`;


class Editor extends React.Component {
    constructor(props) {
        super(props);

        this.switchMode = this.switchMode.bind(this);
        this.onSave = this.onSave.bind(this);
        this.onPropsLoaded = this.onPropsLoaded.bind(this);

        this.state = {editMode: false}
        this.contentRef = React.createRef();
        this.titleRef = React.createRef();
    }

    onPropsLoaded({atUser, bit}) {
        this.setState({
            draft: {title: bit.title, content: bit.content}
        });
        this.titleRef.current.innerText = bit.title;
        this.contentRef.current.innerHTML = marked(bit.content);
    }

    componentDidUpdate(prevProps) {
        if (prevProps.bit.id != this.props.bit.id) {
            this.onPropsLoaded(this.props);
        }
    }

    componentDidMount() {
        this.onPropsLoaded(this.props);
    }

    /** 
     * Saves the current draft of description and content. 
     */
    onSave() {
        // Create an dict with original bit data, then update that with
        // latest changes in draft (e.g. description, content).
        const {bit, atUser} = this.props;
        const updatedBit = Object.assign({}, this.getLatestDraft());
        BitService.update(bit.id, updatedBit)
            .then(resp => Log.info('update resp:', resp))
            .catch(err => Log.error(err))
    }

    /**
     * Returns the most up to date draft. 
     */
    getLatestDraft() {
        // If currently editing we need to grab contents of innerText, as 
        // state.draft only gets explicitly set when we swith to preview mode.
        return this.state.editMode ? {
                title: this.titleRef.current.innerText,
                content: this.contentRef.current.innerText
            } : this.state.draft;
    }

    /**
     * Toggles between editor (only if owner) and preview (default) mode.
     */
    switchMode() {
        // Switch between edit and view
        const isEditMode = !this.state.editMode;
        this.setState({editMode: isEditMode});

        // Get underlying DOM elements for our draft
        const titleEl = this.titleRef.current;
        const contentEl = this.contentRef.current;
        
        // Disable/enable contentEditable
        titleEl.contentEditable = isEditMode;
        contentEl.contentEditable = isEditMode;

        if (isEditMode) {
            contentEl.innerText = this.state.draft.content;
            contentEl.focus();
        } else {
            const content = contentEl.innerText;
            const title = titleEl.innerText;
            this.setState({
                draft: {title: title, content: content}
            });
            contentEl.innerHTML = marked(content);
        }
    }


    render() {
        const {atUser, bit, onDelete} = this.props;

        return <StyledEditor className={this.state.editMode ? 'editor' : 'preview'}>
            <SubHeader>
                <UserProfile atUser={atUser} />
                {atUser.is_auth && <ActionBar>
                    <Action onClick={onDelete} className="danger">Delete</Action>
                    &nbsp; &nbsp;
                    <Action onClick={this.onSave} hidden={!this.state.editMode}>Save</Action>
                    <Action onClick={this.switchMode}>{this.state.editMode ? 'Done' : 'Edit'}</Action>
                </ActionBar>}
            </SubHeader>
            <h1 className="title" placeholder="Enter a title" ref={this.titleRef}></h1>
            <div className="content" placeholder="Enter some markdown" ref={this.contentRef}></div>
        </StyledEditor>                
    }
}

export default Editor;

