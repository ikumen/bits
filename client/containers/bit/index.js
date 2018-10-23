import React from 'react';
import styled from 'styled-components';
import Log from '../../services/logger';
import {Page, SubHeader} from '../../components/layouts';
import UserProfile from '../../components/userprofile';
import BitService from '../../services/bits';
import Utils from '../../services/utils';
import {Title, Tags, Pubdate, Content, Editor} from '../../components/editor';

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

class BitPage extends React.Component {
    constructor(props) {
        super(props);

        this.onUpdate = this.onUpdate.bind(this);
        this.autoSave = this.autoSave.bind(this);
        this.afterAutoSave = this.afterAutoSave.bind(this);
        this.beforeDataLoaded = this.beforeDataLoaded.bind(this);
        this.whenDataLoaded = this.whenDataLoaded.bind(this);
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
            this.props.history.replace(viewUrl)
        } else {
            this.props.history.replace(viewUrl + '/edit')
        }
    }

    /** Helper for props match params. */
    getParams(props) {
        return props && props.match && props.match.params ?
            props.match.params : {};
    }
    
    /** When data is loaded do the following. */
    whenDataLoaded({isAuthUser, bit}) {
        this.setState({
            atUser: bit.user, 
            isAuthUser: isAuthUser,
            // TODO: just too difficult to handle arrays, flatten 
            /// while in editor, join back when saving to backend
            bit: {...{...bit, tags: Utils.flattenArray(bit.tags)}}, 
            savedAt: bit.updated_at,
            updatedAt: bit.updated_at
        });
        return {isAuthUser, bit}; // pass on
    }

    beforeDataLoaded(resp) {
        Log.info('Clearing autoSaveId: ' + this.state.autoSaveId);
        clearInterval(this.state.autoSaveId);
        return resp;
    }

    afterDataLoaded({user, isAuthUser, bit}) {
        if (isAuthUser) {
            const autoSaveId = setInterval(this.autoSave, 120000);
            Log.info('Setting autoSaveId: ' + autoSaveId);
            this.setState({autoSaveId: autoSaveId})    
        }
        return {user, isAuthUser, bit};
    }

    /** Loads main data (atUser, bit) for this component. */
    loadData({atUserId, bitId}) {
        Log.info('atUserId=', atUserId, ', bitId=', bitId)
        BitService.get(atUserId, bitId)
            .then(this.beforeDataLoaded)
            .then(this.whenDataLoaded)
            .then(this.afterDataLoaded)
            .catch(this.props.handleError)
    }

    onUpdate(id, value) {
        Log.info('Updating:', id, '=', value);
        this.setState({
            bit: {...this.state.bit, ...{[id]: value}},
            updatedAt: Utils.toFullISOFormat(new Date())
        });
    }

    afterAutoSave(resp) {
        Log.info('resp=', resp);
        this.setState({savedAt: this.state.updatedAt});
        return resp;
    }

    autoSave(opts) {
        const {bit, lastSavedBit, updatedAt, savedAt, atUser} = this.state;
        if (updatedAt != savedAt && this.isBitModified(bit, lastSavedBit)) {
            Log.info('Changes detected, auto saving ....')
            BitService.update(atUser.id, bit.id, {
                    title: bit.title,
                    pubdate: bit.pubdate, 
                    tags: this.tagsPreprocessor(bit.tags),
                    content: bit.content})
                .then((resp) => {return opts && opts.ignoreResponse ? resp : this.afterAutoSave(resp)})
            .catch(Log.err);
        } else {
            Log.info('No changes detected, skipping auto save');
        }
    }

    isBitModified(bit={}, lastBit={}) {
        return bit.title !== lastBit.title ||
            bit.content !== lastBit.content ||
            bit.pubdate !== lastBit.pubdate ||
            //!Utils.arraysAreEqual(bit.tags, lastBit.tags)
            bit.tags !== lastBit.tags;
    }

    /** Determines if we should reload data, based on new prop match params. */
    shouldReloadData(prevProps, props) {
        const params = this.getParams(props), 
            prevParams = this.getParams(prevProps);
        return prevParams.atUserId != params.atUserId || 
            prevParams.bitId != params.bitId;
    }

    componentWillUnmount() {
        clearInterval(this.state.autoSaveId);
        this.autoSave({ignoreResponse: true});
    }

    componentDidMount() {
        this.loadData({...this.getParams(this.props)});
    }

    componentDidUpdate(prevProps, prevState) {
        Log.debug('prevProps=', prevProps, ', this.props=', this.props);
        if(this.shouldReloadData(prevProps, this.props)) {
            this.loadData({...this.getParams(this.props)});
        } else {
            Log.debug('Not reloading data.')
        }
    }

    pubdatePreprocessor(pubdate) {
        return Utils.toFullISOFormat(pubdate);
    }

    pubdateValidator(pubdate) {
        return (!pubdate || Utils.isValidDate(pubdate));
    }

    tagsPreprocessor(tags) {
        const specialCharsRE = /[^-a-zA-Z0-9,\s]+/g
            , whiteSpaceRE = /\s+/g;
    
        tags = (tags || '').trim()
            .replace(specialCharsRE, '-')
            .replace(whiteSpaceRE, '')
            .split(',')
            .map(a => a.trim())
            .filter(a => a != '');
    
        if (tags.length > 3) {
            Log.warn('More than 3 tags entered,', tags.length-3, 'will be ignored!')
        }
        return tags;
    }

    onDelete() {
        const {atUser, bit} = this.state;
        BitService.delete(atUser.id, bit.id)
            .then(() => this.props.history.replace('/@' + atUser.id))
            .catch(err => Log.error(err))
    }

    render() {
        const {bit={}, atUser, isAuthUser, savedAt, updatedAt} = this.state;
        const editable = this.isEditable(this.props.match.params.edit) && isAuthUser;
        const props = {bitId: bit.id, editable: editable, onUpdate: this.onUpdate}
        return <Page>
            <SubHeader>
                <UserProfile {...this.state} />
                {isAuthUser && 
                <ActionBar>
                    <Action onClick={() => this.onDelete()} className="danger">Delete</Action>
                    <Action onClick={() => this.toggleEditable()}>{editable ? 'Done' : 'Edit'}</Action>
                </ActionBar>}
            </SubHeader>
            <Editor>
                <div className="wrapper">
                <Title {...{...props, value:bit.title}} />
                <div className="meta">
                    <Pubdate {...{...props, 
                        value:bit.pubdate, 
                        preprocessor:this.pubdatePreprocessor, 
                        validator:this.pubdateValidator}} />
                    <Tags {...{...props, value:bit.tags}} /> 
                        {/* preprocessor:this.tagsPreprocessor */}
                </div>
                <Content {...{...props, value:bit.content}} />
                </div>
            </Editor>
        </Page>
    }
}

export {BitPage};