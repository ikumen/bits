import React from 'react';
import BitService from '../../services/bits';
import marked from 'marked';


class Editor extends React.Component {
    constructor(props) {
        super(props);

        this.toggleMode = this.toggleMode.bind(this);
        this.save = this.save.bind(this);
        this.onBitLoaded = this.onBitLoaded.bind(this);

        this.state = {
            userId: props.userId,
            bitId: props.bitId,
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
                content: bit.content
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
        BitService.get(this.state.userId, this.state.bitId)
            .then(this.onBitLoaded)
            .catch(err => console.log(err)); 
    }

    save() {
        /* If in middle of edit, get latest updates, as only toggle 
        to preview will explicitly updated draft with latest updates */
        const draft = this.state.editMode ? 
            this.getLatestEditsAsDraft() : this.state.draft;

        // Create updated bit from original bit, and changes in draft
        const updatedBit = Object.assign(this.state.bit, draft);
        BitService.save(this.state.userId, updatedBit)
            .then(this.onBitLoaded)
            .catch(err => console.log(err))
    }

    getLatestEditsAsDraft() {
        return {
            description: this.descriptionRef.current.innerText,
            content: this.contentRef.current.innerText
        }
    }

    toggleMode() {
        // Switch to new mode (e.g. edit or preview)
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
        return <div>
            {!this.state.viewOnly && <div>
                <button onClick={this.toggleMode}>{this.state.editMode ? 'Preview' : 'Edit'}</button>
                <button onClick={this.save}>Save</button>
            </div>}
            <h1 ref={this.descriptionRef}></h1>
            <div ref={this.contentRef}></div>
        </div>
    }
}

export default Editor;

