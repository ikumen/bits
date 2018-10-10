import React from 'react';
import BitService from '../../services/bits';
import styled from 'styled-components';
import {Link} from 'react-router-dom';
import UserService from '../../services/user';
import Editor from '../../components/editor';
import Log from '../../services/logger';
import Utils from '../../services/utils';
import UserProfile from '../../components/userprofile';
import {Page, SubHeader, If} from '../../components/layouts';
import marked from 'marked';


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
    #title.edit, #content.edit, #pubdate.edit, #tags.edit {
        outline: none;
        opacity: 1;
        background: #F8F4E3;
    }

    & #title {
        font-size: 2rem;
        font-weight: 500;
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
        margin-right: 20px;
    }
    & #tags {
        text-align: right;
    }
    & .meta .view, & .meta i  {
        color: #bbb;
    }
`;

const EditStatus = styled.div`
    color: #bbb;
    font-size: .8rem;
    display: flex;
    flex-direction: row-reverse;
`;

class BitPage extends React.Component {
    constructor(props) {
        super(props);
        
        this.onDelete = this.onDelete.bind(this);
        this.switchMode = this.switchMode.bind(this);
        this.setStateWithParams = this.setStateWithParams.bind(this);
        this.onUpdate = this.onUpdate.bind(this);
        this.loadBit = this.loadBit.bind(this);
        this.saveIfModified = this.saveIfModified.bind(this);
        this.loadBitComplete = this.loadBitComplete.bind(this);

        this.setStateWithParams(props.match.params);
    }

    saveIfModified() {
        console.log('---------draft====>', this.state.draft);
        if (this.state.savedAt != this.state.updatedAt) {
            Log.info('===> changes detected, saving ....');
            BitService.update(this.state.bitId, this.state.draft)
                .then(resp => {
                    Log.info('saved ', resp);
                    this.setState({savedAt: this.state.updatedAt});
                })
                .catch(err => Log.err(err));
            
        } else {
            Log.info('===> No change, skipping save!');
        }
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
                pubdate: bit.pubdate,
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

    componentDidMount() {
        this.loadBit(this.state.atUserId, this.state.bitId);
        const autoSaveId = setInterval(this.saveIfModified, 20000);
        this.setState({autoSaveId: autoSaveId});
    }

    componentWillUnmount() {
        clearInterval(this.state.autoSaveId);
    }

    onDelete() {
        BitService.delete(this.state.bit.id)
            .then(() => this.props.history.replace('/@' + this.state.atUserId))
            .catch(err => Log.error(err))
    }

    onUpdate(draft) {
        Log.info('Updating:', draft);
        const prevDraft = this.state.draft;
        this.setState({
            draft: {
                title: 'title' in draft ? draft.title : prevDraft.title,
                content: 'content' in draft ? draft.content : prevDraft.content,
                pubdate: 'pubdate' in draft ?  draft.pubdate : prevDraft.pubdate,
                tags: 'tags' in draft ? draft.tags : prevDraft.tags},
            updatedAt: Utils.toFullISOFormat(new Date())
        })
    }

    pubdatePreprocessor(pubdate) {
        return Utils.toFullISOFormat(pubdate);
    }
    
    tagsPreprocessor(tags) {
        const specialCharsRE = /[^-a-zA-Z0-9,\s]+/g
            , whiteSpaceRE = /\s+/g;
    
        tags = (tags || '').trim()
            .replace(specialCharsRE, '-')
            .replace(whiteSpaceRE, '')
            .split(',')
            .filter(a => a != '');
    
        if (tags.length > 3) {
            Log.warn('More than 3 tags entered,', tags.length-3, 'will be ignored!')
            return tags.slice(0, 3);
        }
        return tags;
    }

    render() {
        const {atUser, editMode, draft} = this.state;
        console.log('====== rerendering ....', draft)
        const props = {editMode: editMode, onUpdate: this.onUpdate}
        return <Page>
            <SubHeader>
                <UserProfile atUser={atUser} />
                {atUser && atUser.is_auth && 
                <ActionBar>
                    <Action onClick={this.onDelete} className="danger">Delete</Action>
                    &nbsp; &nbsp;
                    <Action onClick={this.switchMode}>{editMode ? 'Done' : 'Edit'}</Action>
                </ActionBar>}
            </SubHeader>
            {draft &&
            <StyledEditor>
                <Title value={draft.title} editMode={editMode} onUpdate={this.onUpdate}/>
                <div className="meta">
                    <Pubdate value={draft.pubdate} editMode={editMode} onUpdate={this.onUpdate}
                        preprocessor={this.pubdatePreprocessor} validator={Utils.isValidDate} />
                    <Tags value={draft.tags} editMode={editMode} onUpdate={this.onUpdate} 
                        preprocessor={this.tagsPreprocessor} />
                </div>
                <Content value={draft.content} editMode={editMode} onUpdate={this.onUpdate} 
                    renderer={marked} />
            </StyledEditor>
            }
            <EditStatus> 
                Last: &nbsp; 
                <div>saved  {this.state.savedAt}</div> &nbsp; / &nbsp; 
                <div>updated {this.state.updatedAt}</div>
            </EditStatus>
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
        this.setValue(this.props);
    }

    componentDidUpdate(prevProps) {
        this.setValue(this.props);
    }

    setValue({value, editMode, renderer}) {
        if (editMode) {
            this.elementRef.current.innerText = value;
        } else {
            this.elementRef.current.innerHTML = renderer ? renderer(value) : value;
        }
    }

    onInput(e) {
        const {validator, preprocessor, onUpdate} = this.props;
        const value = e.target.innerText;
        if (!validator || validator(value)) {
            onUpdate({[this.props.id]: (preprocessor ? preprocessor(value) : value)});
        } else {
            Log.info('Invalid input!')
        }
    }

    render() {
        const {id, editMode, placeholder} = this.props;
        console.log('====editable rerender: editMode=', editMode)
        return <div id={id} 
            className={editMode ? 'edit' : 'view'}
            contentEditable={editMode}
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
        <i className="icon-calendar"></i>
        <Editable id="pubdate" {...{...props, value: value ? Utils.toSimpleISOFormat(value) : ''}} 
            placeholder="e.g, YYYY-MM-DD"/>
    </React.Fragment>
);

const Tags = ({value, ...props}) => (
    <React.Fragment>
        <i className="icon-tags"></i>
        <Editable id="tags" {...{...props, value: Utils.flattenArray(value)}}  
            placeholder="e.g, java, spring-jpa (comma separated, 3 max)"/>
    </React.Fragment>
);

const Content = (props) => (
    <Editable id="content" {...props} placeholder="e.g, Enter your markdown"/>
);

export {BitPage};
