import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Editor from '../../components/editor';
import Log from '../../services/logger';
import {Page} from '../../components/layouts';


class BitPage extends React.Component {
    constructor(props) {
        super(props);
        
        this.onDelete = this.onDelete.bind(this);
        this.switchMode = this.switchMode.bind(this);
        this.setStateWithParams = this.setStateWithParams.bind(this);
        this.onUpdate = this.onUpdate.bind(this);
        this.loadBit = this.loadBit.bind(this);
        this.loadBitComplete = this.loadBitComplete.bind(this);

        this.setStateWithParams(props.match.params);
    }

    getEditMode(editParam) {
        return editParam === 'edit';
    }

    setStateWithParams(params) {
        this.state = {
            atUserId: params.atUserId,
            bitId: params.bitId,
            editMode: this.getEditMode(params.edit)
        }
    }

    componentDidUpdate(prevProps) {
        const params = this.props.match.params
            , prevParams = prevProps.match.params;

        /* We only care about two state updates:
            - bitId, when we want to load a new bit
            - edit, when we switch between edit/view mode for a bit */
        if (prevParams.bitId != params.bitId) {
            this.setStateWithParams(params);
            this.loadBit(params.atUserId, params.bitId)
        } else if (prevParams.edit !== params.edit) {
            this.setState({editMode: this.getEditMode(params.edit)});
        }        
    }

    loadBit(atUserId, bitId) {
        Log.info('Loading bit', bitId)
        Promise.all([
                UserService.getAtUser(atUserId),
                BitService.get(bitId)])
            .then(([atUser, bit]) => this.loadBitComplete(atUser, bit))
            .catch(err => Log.error(err));
    }

    loadBitComplete(atUser, bit) {
        Log.info('atUser=', atUser, ', bit=', bit)
        this.setState({
            atUser: atUser,
            bit: bit,
            draft: {
                title: bit.title,
                content: bit.content,
                pubdate: bit.published_at,
                tags: bit.tags},
            updatedAt: bit.updated_at,
            savedAt: bit.updated_at,
        })
    }

    switchMode() {
        const viewUrl = '/@' + this.state.atUserId + '/bits/' + this.state.bitId;
        if (this.state.editMode) {
            this.props.history.push(viewUrl)
        } else {
            this.props.history.push(viewUrl + '/edit')
        }
    }

    componentDidUpdate(prevProps) {
        Log.info('updating', 'prevProps=', prevProps, ', props=', this.props)
    }

    componentDidMount() {
        this.loadBit(this.state.atUserId, this.state.bitId);
    }

    onDelete() {
        BitService.delete(this.state.bit.id)
            .then(() => this.props.history.replace('/@' + this.state.atUserId))
            .catch(err => Log.error(err))
    }

    onUpdate(draft) {
        const prevDraft = this.state.draft;
        this.setState({
            draft: {
                title: 'title' in draft ? draft.title : prevDraft.title,
                content: 'content' in draft ? draft.content : prevDraft.content,
                //pubdate: 'pubdate' in draft ?  draft.pubdate : prevDraft.pubdate,
                tags: 'tags' in draft ? draft.tags : prevDraft.tags
            },
            updatedAt: new Date()
        })
    }

    render() {
        console.log('rendering ....', this.state.draft)
        return <Page>
            {/* {this.state.atUser && 
                <Editor bit={this.state.bit} 
                    onDelete={this.onDelete} 
                    atUser={this.state.atUser} 
                    editMode={this.state.editMode && this.state.atUser.is_auth}
                    switchMode={this.switchMode}
                />
            } */}
            {this.state.draft && <_Editor draft={this.state.draft} onUpdate={this.onUpdate}></_Editor>}
            hi-ho
        </Page>
    }
}

class Editable extends React.Component {
    constructor(props) {
        super(props);

        this.onInput = this.onInput.bind(this);
        this.setValue = this.setValue.bind(this);
        this.elementRef = React.createRef();
    }

    componentDidMount() {
        Log.info('value=', this.props.value)
        this.setValue(this.props.value);
    }

    setValue(value) {
        Log.info('value=', value)
        this.elementRef.current.innerText = value;
    }

    onInput(e) {
        const {validator, preprocessor, onChange} = this.props;
        const value = e.target.innerText;
        if (!validator || validator(value)) {
            onChange(this.props.id, (preprocessor ? preprocessor(value) : value));
        } else {
            Log.info('Invalid input!')
        }
    }

    render() {
        return <div 
            id={this.props.id}
            contentEditable={true}
            placeholder={this.props.placeholder}
            onInput={this.onInput}
            ref={this.elementRef}>
        </div>
    }
}

class Content extends React.Component {
    constructor(props) {
        super(props);

        this.setValue = this.setValue.bind(this);
        this.elementRef = React.createRef();
    }

    componentDidMount() {
        this.setValue(this.props.preRender(this.props.value));
    }

    setValue(value) {
        this.elementRef.current.innerHTML = value;
    }

    render() {
        return <div
            id={this.props.id}
            contentEditable={false}
            placeholder={this.props.placeholder}
            ref={this.elementRef}>
        </div>
            
    }
}

const StyledEditor = styled.div`
    .title {
        font-size: 2rem;
    }
    & [contenteditable=true]:empty:before {
        content: attr(placeholder);
        opacity: .2;
        display: block; /* For Firefox */
    }

`;

class _Editor extends React.Component {
    constructor(props) {
        super(props);

       this.onChange = this.onChange.bind(this);
       this.pubdateValidator = this.pubdateValidator.bind(this);
       this.preprocessTags = this.preprocessTags.bind(this);

    }

    onChange(id, value) {
        Log.info(id, 'changed:', value)
        this.props.onUpdate({[id]: value});
    }

    flattenArray(arr) {
        return arr.join(', ')
    }

    preprocessTags(tags) {
        const specialCharsRE = /[^-a-zA-Z0-9,\s]+/g
            , whiteSpaceRE = /\s+/g;

        tags = (tags || '').trim()
            .replace(specialCharsRE, '-')
            .replace(whiteSpaceRE, '')
            .split(',');

        if (tags.length > 3) {
            Log.warn('More than 3 tags entered,', tags.length-3, 'will be ignored!')
            return tags.slice(0, 3);
        }
        return tags;
    }

    pubdateValidator(pubdate) {
        if (isNaN(Date.parse(pubdate))) 
            return false;        
        // we already have valid date, just make 
        // sure it's in the format we want yyyy-mm-dd
        const re = /(\d{4})-(\d{2})-(\d{2})/;
        const m = re.exec(pubdate);
        return m && m.length == 4;
    }

    render() {
        const draft = this.props.draft;
        console.log(draft)
        return <StyledEditor>
            <Editable id="title" onChange={this.onChange} 
                placeholder="Enter a title" 
                value={draft.title} />
            <div className="meta">
                <Editable id="pubdate" onChange={this.onChange} 
                    placeholder="e.g, 2018-12-30" 
                    validator={this.pubdateValidator}  
                    value={draft.pubdate} />
                <div className="spaver"></div>
                <Editable id="tags" onChange={this.onChange} 
                    placeholder="e.g, java, spring-framework, jpa" 
                    preprocess={this.preprocessTags} 
                    value={this.flattenArray(draft.tags)} />
            </div>
            <Editable id="content" onChange={this.onChange} 
                    placeholder="e.g, Enter your markdown" 
                    value={draft.content} />
        </StyledEditor>
    }
}

export {BitPage};
