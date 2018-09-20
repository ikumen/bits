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
    font-size: .8rem;
    padding: 3px 12px;
    cursor: pointer;

    &.danger {
        background-color: red;
        color: #fff;
        opacity: .6;
    }
`;
        // margin-bottom: 10px;

const StyledEditor = styled.div`
    margin-bottom: 40px;
    padding: 0;
    margin: 0;
    &.editor .content, &.editor .description {
        outline: none;
        background: #F8F4E3;
    }
`;


class Editor extends React.Component {
    constructor(props) {
        super(props);

        this.toggleMode = this.toggleMode.bind(this);
        this.save = this.save.bind(this);
        this.delete = this.delete.bind(this);
        this.onBitLoaded = this.onBitLoaded.bind(this);

        this.state = {
            viewOnly: props.viewOnly,
            editMode: false,
        };

        this.contentRef = React.createRef();
        this.descriptionRef = React.createRef();
    }

    onBitLoaded(bit) {
        this.setState({
            bit: bit,
            draft: {
                description: bit.description,
                content: bit.content.trim() === '_' ? '' : bit.content
            }
        });

        this.descriptionRef.current.innerText = bit.description;
        this.contentRef.current.innerHTML = marked(bit.content);
    }

    componentDidUpdate(prevProps) {
        if (this.props.viewOnly !== prevProps.viewOnly) {
            this.setState({viewOnly: this.props.viewOnly})
        }
    }

    componentDidMount() {
        BitService.get(this.props.bitId)
            .then(this.onBitLoaded)
            .catch(err => Log.error(err)); 
    }

    save() {
        /* If in middle of edit, get latest updates, as only toggle 
        to preview will explicitly updated draft with latest updates */
        const draft = this.state.editMode ? 
            this.getLatestEditsAsDraft() : this.state.draft;

        // Create updated bit from original bit, and changes in draft
        const updatedBit = Object.assign(this.state.bit, draft);
        BitService.update(updatedBit)
            .then(bit => Log.info('Updated: ', bit))
            .catch(err => Log.error(err))
    }

    delete() {
        BitService.delete(this.state.bit._id)
            //TODO: redirect to /@user
            .then(resp => Log.info('deleted', resp))
            .catch(err => Log.error(err))
    }

    getLatestEditsAsDraft() {
        return {
            description: this.descriptionRef.current.innerText,
            content: this.contentRef.current.innerText
        }
    }

    toggleMode() {
        // Switch between edit and view
        const isEditMode = !this.state.editMode;
        this.setState({editMode: isEditMode});

        // Get underlying DOM elements for our draft
        const descriptionEl = this.descriptionRef.current;
        const contentEl = this.contentRef.current;
        
        descriptionEl.contentEditable = isEditMode;
        contentEl.contentEditable = isEditMode;

        if (isEditMode) {
            contentEl.innerText = this.state.draft.content;
            contentEl.focus();
        } else {
            const content = contentEl.innerText;
            const description = descriptionEl.innerText;
            this.setState({
                draft: {description: description, content: content}
            });
            contentEl.innerHTML = marked(content);
        }
    }


    render() {
        return <StyledEditor className={this.state.editMode ? 'editor' : 'preview'}>
            <SubHeader>
                <UserProfile user={this.props.user} />
                {!this.state.viewOnly && <ActionBar>
                    <Action onClick={this.delete} className="danger">Delete</Action>
                    &nbsp; &nbsp;
                    <Action onClick={this.save} hidden={!this.state.editMode}>Save</Action>
                    <Action onClick={this.toggleMode}>{this.state.editMode ? 'Done' : 'Edit'}</Action>
                </ActionBar>}
            </SubHeader>
            <h1 className="description" ref={this.descriptionRef}></h1>
            <div className="content" ref={this.contentRef}></div>
        </StyledEditor>
    }
}

export default Editor;

