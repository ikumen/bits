import React from 'react';
import {Link} from 'react-router-dom';
import BitService from '../../services/bits';
import marked from 'marked';
import Log from '../../services/logger';
import Utils from '../../services/utils';
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
    padding: 0;
    margin: 0;
    &.editor .content, &.editor .title, &.editor .tags, &.editor .publishedAt  {
        outline: none;
        opacity: 1;
        background: #F8F4E3;
    }
    &[contenteditable=true]:empty:before {
        content: attr(placeholder);
        display: block; /* For Firefox */
    }
    & .meta {
        margin: -20px 0 40px;
        width: 100%;
        display: flex;
        flex-direction: row;
    }
    & .spacer {
        flex: 1;
    }
    & .publishedAt {
        flex: 9;
    }
    & .tags {
        flex: 20;
        text-align: right;
    }
    &.preview .meta {
        color: #bbb;
    }
`;



class Editor extends React.Component {
    constructor(props) {
        super(props);

        this.onSwitchMode = this.onSwitchMode.bind(this);
        this.onSave = this.onSave.bind(this);
        this.onPropsLoaded = this.onPropsLoaded.bind(this);

        this.contentRef = React.createRef();
        this.titleRef = React.createRef();
        this.tagsRef = React.createRef();
        this.publishedAtRef = React.createRef();
    }

    onPropsLoaded({atUser, bit, editMode}) {
        const draft = {
            title: bit.title, 
            content: bit.content,
            published_at: Utils.formatDateString(bit.published_at),
            tags: bit.tags ? bit.tags.join(', ') : ''
        }
        this.setState({draft: draft});
        this.titleRef.current.innerText = draft.title;

        if (editMode) {
            this.contentRef.current.innerText = draft.content;
            this.publishedAtRef.current.innerText = draft.published_at;
            this.tagsRef.current.innerText = draft.tags;
        } else {
            this.contentRef.current.innerHTML = marked(draft.content);
            this.publishedAtRef.current.innerHTML = this.formatPublishedDate(draft.published_at === '' ? 'Draft' : draft.published_at);
            this.tagsRef.current.innerHTML = this.formatTags(draft.tags);
        }
    }

    formatTags(tags) {
        return '<div><i class="icon-tags"></i> ' + tags + '</div>'
    }

    formatPublishedDate(pubdate) {
        return '<time dateTime="' + pubdate + '"><i class="icon-calendar"></i> ' + pubdate + '</time>';
    }

    componentDidUpdate(prevProps) {
        if (prevProps.bit.id != this.props.bit.id) {
            this.onPropsLoaded(this.props);
        } else if (prevProps.editMode !== this.props.editMode) {
            this.onSwitchMode(this.props.editMode);
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
        const {bit, atUser, editMode} = this.props;
        const updatedBit = editMode ? this.getDraftFromContentEditables() : this.state.draft;
        updatedBit.published_at = updatedBit.published_at.trim() === '' ? '' : updatedBit.published_at + 'T00:00:00Z' // hack to append time+zone
        updatedBit.tags = updatedBit.tags ? updatedBit.tags.split(',').map((s)=>{return s.trim()}) : [];
        BitService.update(bit.id, updatedBit)
            .then(resp => Log.info('update resp:', resp))
            .catch(err => Log.error(err))
    }

    getDraftFromContentEditables() {
        return {
            title: this.titleRef.current.innerText,
            content: this.contentRef.current.innerText,
            tags: this.tagsRef.current.innerText,
            published_at: this.publishedAtRef.current.innerText === '' ?
                '' : this.publishedAtRef.current.innerText
        }
    }

    /**
     * Handles loading/unloading between editor and preview mode.
     */
    onSwitchMode(editMode) {
        let draft = this.state.draft;
        if (editMode) {
            this.contentRef.current.innerText = draft.content;
            this.publishedAtRef.current.innerText = draft.published_at; 
            this.tagsRef.current.innerText = draft.tags;
            this.contentRef.current.focus();
        } else {
            draft = this.getDraftFromContentEditables();
            this.setState({draft: draft});
            this.publishedAtRef.current.innerHTML = this.formatPublishedDate(this.publishedAtRef.current.innerText.trim() === '' ? 'Draft' : this.publishedAtRef.current.innerText); 
            this.contentRef.current.innerHTML = marked(this.contentRef.current.innerText);
            this.tagsRef.current.innerHTML = this.formatTags(draft.tags);
        }
    }


    render() {
        const {atUser, bit, onDelete, editMode, switchMode} = this.props;
        return <StyledEditor className={editMode ? 'editor' : 'preview'}>
            <SubHeader>
                <UserProfile atUser={atUser} />
                {atUser.is_auth && <ActionBar>
                    <Action onClick={onDelete} className="danger">Delete</Action>
                    &nbsp; &nbsp;
                    <Action onClick={this.onSave} hidden={!editMode}>Save</Action>
                    <Action onClick={switchMode}>{editMode ? 'Done' : 'Edit'}</Action>
                </ActionBar>}
            </SubHeader>
            <h1 className="title" contentEditable={editMode} placeholder="Enter a title" ref={this.titleRef}></h1>
            <div className="meta">
                <div className="publishedAt" contentEditable={editMode} placeholder="e.g, 2016-01-17" ref={this.publishedAtRef}></div>
                <div className="spacer"></div>
                <div className="tags" contentEditable={editMode} placeholder="e.g, java,react" ref={this.tagsRef}></div>
            </div>
            <div className="content" contentEditable={editMode} placeholder="Enter some markdown" ref={this.contentRef}></div>
        </StyledEditor>                
    }
}

export default Editor;

