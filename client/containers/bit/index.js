import React from 'react';
import styled from 'styled-components';
import Log from '../../services/logger';
import {Page} from '../../components/layouts';
import UserService from '../../services/user';
import BitService from '../../services/bits';
import Utils from '../../services/utils';

const Editor = styled.div`
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

class BitPage extends React.Component {
    constructor(props) {
        super(props);

        this.onUpdate = this.onUpdate.bind(this);
        this.autoSave = this.autoSave.bind(this);
        this.beforeDataLoaded = this.beforeDataLoaded.bind(this);
        this.afterDataLoaded = this.afterDataLoaded.bind(this);
        this.state = {}
    }

    /** Helper for enabling editable flag if url 'edit' param is present. */
    isEditable(editParam) {
        return editParam === 'edit';
    }

    /** Toggle between edit and view modes. */
    toggleEditable() {
        const {atUserId, bitId, edit} = this.getParams(this.props);
        const viewUrl = '/@' + atUserId + '/bits/' + bitId;
        if (this.isEditable(edit)) {
            this.props.history.push(viewUrl)
        } else {
            this.props.history.push(viewUrl + '/edit')
        }
    }

    /** Helper for props match params. */
    getParams(props) {
        return props && props.match && props.match.params ?
            props.match.params : {};
    }
    
    /** When data is loaded do the following. */
    whenDataLoaded(atUser, bit) {
        this.setState({
            atUser: atUser, 
            bit: bit,
            savedAt: bit.updated_at,
            updatedAt: bit.updated_at
        });
        return [atUser, bit];
    }

    beforeDataLoaded(resp) {
        Log.info('Clearing autoSaveId: ' + this.state.autoSaveId);
        clearInterval(this.state.autoSaveId);
        return resp;
    }

    afterDataLoaded(resp) {
        const autoSaveId = setInterval(this.autoSave, 20000);
        Log.info('Setting autoSaveId: ' + autoSaveId);
        this.setState({autoSaveId: autoSaveId})
        return resp;
    }

    /** Loads main data (atUser, bit) for this component. */
    loadData({atUserId, bitId}) {
        Log.info('atUserId=', atUserId, ', bitId=', bitId)
        Promise.all([
            UserService.getAtUser(atUserId),
            BitService.get(bitId)
        ]).then((resp) => this.beforeDataLoaded(resp))
        .then((resp) => this.whenDataLoaded(...resp))
        .then((resp)=> this.afterDataLoaded(resp))
        .catch(err => Log.error(err));
    }

    onUpdate(id, value) {
        Log.info('Updating:', id, '=', value);
        this.setState({
            bit: {...this.state.bit, ...{[id]: value}},
            updatedAt: Utils.toFullISOFormat(new Date())
        });
    }

    autoSave() {
        const {bit, lastSavedBit, updatedAt, savedAt} = this.state;
        if (updatedAt != savedAt && this.isBitModified(bit, lastSavedBit)) {
            Log.info('Changes detected, auto saving ....')
        } else {
            Log.info('No changes detected, skipping auto save');
        }
    }

    isBitModified(bit={}, lastBit={}) {
        return bit.title !== lastBit.title ||
            bit.content !== lastBit.content ||
            bit.pubdate !== lastBit.pubdate ||
            !Utils.arraysAreEqual(bit.tags, lastBit.tags);
    }

    /** Determines if we should reload data, based on new prop match params. */
    shouldReloadData(prevProps, props) {
        const params = this.getParams(props), 
            prevParams = this.getParams(prevProps);
        return prevParams.atUserId != params.atUserId || 
            prevParams.bitId != params.bitId;
    }

    bitToString(bit) {
        return 'bit[' +
            'title=' + bit.title + ',\n' +
            'pubdate=' + bit.pubdate + ',\n' +
            'tags=' + bit.tags + ']\n';
    }

    componentDidMount() {
        Log.info('-->');
        this.loadData({...this.getParams(this.props)});
    }

    componentDidUpdate(prevProps, prevState) {
        Log.info('--> prevProps=', prevProps, ', props=', this.props, ', prevState=', prevState, ', state=', this.state);
        if(this.shouldReloadData(prevProps, this.props)) {
            this.loadData({...this.getParams(this.props)});
        }
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
        }
        return tags;
    }

    render() {
        Log.info('---> ')
        const {atUserId, bitId, edit} = this.getParams(this.props);
        const {bit = {}, savedAt, updatedAt} = this.state;
        const editable = this.isEditable(edit);
        return <Page>
            <button onClick={()=> this.toggleEditable()}>{editable ? 'done' : 'edit'}</button>
            <br/>
            atUser: {atUserId} <br/>
            bitId: {bitId} <br/>
            isEdit: {editable ? 'true' : 'false'}<br/>
            updatedAt/savedAt: {savedAt} / {updatedAt} <br/>
            <hr/>
            <Editor>
            <Title value={bit.title} bitId={bit.id} editable={editable} onUpdate={this.onUpdate} /> <br/>
            <Pubdate value={bit.pubdate} bitId={bit.id} editable={editable} onUpdate={this.onUpdate}
                preprocessor={this.pubdatePreprocessor} validator={Utils.isValidDate} /><br/>
            <Tags value={bit.tags} editable={editable} onUpdate={this.onUpdate} 
                preprocessor={this.tagsPreprocessor} />
            </Editor>
            <pre>
                {this.bitToString(bit)}
            </pre>

        </Page>
    }
}

class Editable extends React.Component {
    constructor(props) {
        super(props);

        this.onInput = this.onInput.bind(this);
        this.setValue = this.setValue.bind(this);
        this.elementRef = React.createRef();
        this.state = {
            defaultValue: '',
            hasErrors: false
        }
    }

    componentDidMount() {
        this.setValue(this.props);
    }

    componentDidUpdate(prevProps) {
        console.log('prev=', prevProps, ', props=', this.props)
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

    setValue({value, editable, renderer}) {
        if (editable) {
            this.elementRef.current.innerText = value;
        } else {
            this.elementRef.current.innerHTML = renderer ? renderer(value) : value;
        }
    }

    onInput(e) {
        const {validator, preprocessor, onUpdate, editable, renderer} = this.props;
        const value = e.target.innerText;
        if (!validator || validator(value)) {
            this.setState({hasErrors: false})
            onUpdate(this.props.id, (preprocessor ? preprocessor(value) : value));
        } else {
            this.setState({hasErrors: true})
            Log.info('Invalid input!')
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
        <i className="icon-calendar"></i>
        <Editable id="pubdate" {...{...props, value: value ? Utils.toSimpleISOFormat(value) : value}} 
            placeholder="e.g, YYYY-MM-DD"/>
    </React.Fragment>
);

const Tags = ({value, ...props}) => (
    <React.Fragment>
        <i className="icon-tags"></i>
        <Editable id="tags" {...{...props, value: Utils.flattenArray(value)}}
            defaultValue={[]}
            isEqual={Utils.arraysAreEqual}
            placeholder="e.g, java, spring-jpa (comma separated, 3 max)"/>
    </React.Fragment>
);

const Content = (props) => (
    <Editable id="content" {...props} placeholder="e.g, Enter your markdown"/>
);

export {BitPage};