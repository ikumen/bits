import React from 'react';

import BitService from '../../services/bits';
import Utils from '../../services/utils';
import UserProfile from '../../components/userprofile';
import { Page, SubHeader } from '../../components/layouts';
import { markedWithHljs } from '../../services/renderers';


function asBitPage(Cpnt) {
  return class extends React.Component {
    constructor(props) {
      super(props);

      console.log(props);
      this.getParams = this.getParams.bind(this);
      this.loadBit = this.loadBit.bind(this);
      this.handleBit = this.handleBit.bind(this);
      this.state = {}
    }

    loadBit({atUserId, bitId}) {
      BitService.get(atUserId, bitId)
        .then(this.handleBit)
        .catch(this.props.handleError);
    }

    handleBit({isAuthUser, bit}) {
      console.log('handling bit: ', bit)
      this.setState({
        atUser: bit.user,
        isAuthUser: isAuthUser,
        bit: {...{...bit, tags: Utils.flattenArray(bit.tags)}},
        savedAt: bit.updated_at,
        updatedAt: bit.updated_at,  
      });
    }

    componentDidMount() {
      this.loadBit(this.getParams());
    }

    getParams() {
      return this.props.match.params;
    }

    render() {
      const { isAuthUser, actions } = this.props;
      return <Page>
        <SubHeader>
          <UserProfile {...this.state} />
          { (isAuthUser && actions) && 
            <ActionBar>
              { actions }
            </ActionBar> }
        </SubHeader>
        <Cpnt {...this.state} />
      </Page>;
    }
  }
}

const Editor = (props) => {
  const { bit={}, isAuthUser } = props;
  return <CMEditor
    content={bit.content}
    className={isAuthUser ? '' : 'hidden' }
  />
}

const Viewer = (props) => {
  const { bit={} } = props;
  return <React.Fragment>
    <h1>{bit.title}</h1>
    <div dangerouslySetInnerHTML={{__html: markedWithHljs(bit.content || '')}} />
  </React.Fragment>;
}

const BitEditorPage = asBitPage(Editor);
const BitViewerPage = asBitPage(Viewer);

import CodeMirror from 'codemirror';
import style from 'codemirror/lib/codemirror.css';
require('codemirror/mode/gfm/gfm');
import css from './index.css';

class CMEditor extends React.Component {
  constructor(props) {
    super(props);

    this.editorRef = React.createRef();
  }

  componentDidMount() {
    this.codemirror = CodeMirror.fromTextArea(this.editorRef.current, {
      autofocus: true,
      mode: 'gfm',
      lineWrapping: true,
      viewportMargin: Infinity,
    });
    this.codemirror.setValue(this.props.content || '')
  }

  componentDidUpdate() {
    this.codemirror.setValue(this.props.content || '')
  }

  render() {
    return <textarea className="CodeMirror" ref={this.editorRef} />
  }
}


export {BitEditorPage, BitViewerPage};
