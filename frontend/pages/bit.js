import React from 'react';
import { Link } from 'react-router-dom';
import CodeMirror from 'codemirror';
import 'codemirror/lib/codemirror.css';
import 'codemirror/mode/gfm/gfm';
import 'codemirror/addon/display/placeholder';
import 'highlight.js/styles/github-gist.css';

import { Page } from '../components';
import { BitService, getDateParts, MarkedWithHljs } from '../services';


class BitPage extends React.Component {  
  constructor(props) {
    super(props)
    this.state = {bit:{}}
    this.onChange = this.onChange.bind(this);
    this.onSave = this.onSave.bind(this);
    this.onSaveSuccess = this.onSaveSuccess.bind(this);
    this.onDelete = this.onDelete.bind(this);
    this.loadBit = this.loadBit.bind(this);
  }

  componentDidMount() {
    this.loadBit(this.props.match.params.id)    
  }

  loadBit(id) {
    if (id === 'new') {
      this.setState({
        bit: {id: 'new', description: '', content: ''}, 
        status: ''
      });
    } else {
      BitService.get(id)
        .then(bit => this.setState({bit}))
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevProps.match.params.id !== this.props.match.params.id) {
      this.loadBit(this.props.match.params.id);
    }
  }

  onChange({description, content}) {
    const { bit } = this.state;
    if (description !== undefined) {
      bit.description = description;
    }
    if (content !== undefined) {
      bit.content = content;
    }
    this.setState({ bit })
    if (this.autoSaveId) {
      this.setState({status: 'Changes detected ...'}); 
      clearTimeout(this.autoSaveId);
    }
    this.autoSaveId = setTimeout(this.onSave, 3000);
  }

  onSaveSuccess(prevBit, nextbit) {
    this.setState({status: 'Changes saved'}); 
    if (prevBit.id != nextbit.id) {
      this.props.history.replace(`/bits/${nextbit.id}/edit`);
    }
  }

  onSave() {
    const {user} = this.props;
    if (user && user.authenticated) {
      this.setState({status: 'Saving changes ...'}); 
      const { bit } = this.state;
      BitService.save(bit)
          .then(savedBit => this.onSaveSuccess(bit, savedBit));
    }
  }

  componentWillUnmount() {
    const { bit } = this.state;
    if (bit.id !== 'new' && this.props.match.params.edit === 'edit') {
      if (this.autoSaveId) {
        clearTimeout(this.autoSaveId);
      }
      BitService.save(bit);
    }
  }

  onDelete() {
    const { bit } = this.state;
    if (bit.id === 'new') { 
      // treat like cancel
      this.props.history.replace('/');
    } else {
      BitService.delete(bit.id)
      .then(() => this.props.history.replace('/'));
    }
  }

  render() {
    const isEdit = this.props.match.params.edit === 'edit';
    const { user={} } = this.props;
    const { bit, status } = this.state;
    const { year, monthDay } = getDateParts(bit.created_at);
    return <Page>
      <section className="flex items-center pa0 pt3">
        {(bit && user.authenticated) && 
          <menu className="flex items-end flex-row-reverse pa0 w-100">
            <button className="f6 pa2 ml3 bw0 dib red outline" onClick={this.onDelete}>Delete</button>
            <MarkdownBtn bit={bit} isEdit={isEdit} />
            <Status status={status} isEdit={isEdit} />
          </menu>}
      </section>

      {isEdit ? 
        <Editor bit={bit} onChange={this.onChange} onSave={this.onSave} />
        : <Viewer bit={bit} user={user} />
      }
    </Page>
  }
}

const Status = ({status, isEdit}) => (
  isEdit ? <div className="f6 pa2 pb0 ma0 lighter-gray i">{status}</div> : ''
);

const MarkdownBtn = ({bit, isEdit}) => (
  <Link className={`f6 link pa2 dib white ${isEdit ? 'bg-light-blue' : 'bg-blue'}`} 
    to={`/bits/${bit.id}${isEdit ? '' : '/edit'}`} 
    replace={true}>Markdown</Link>
);

class Editor extends React.Component {
  constructor(props) {
    super(props);
    this.descriptionRef = React.createRef();
    this.editorRef = React.createRef();
    this.onContentChange = this.onContentChange.bind(this);
    this.onDescriptionChange = this.onDescriptionChange.bind(this);
  }

  componentDidMount() {
    this.codemirror = CodeMirror.fromTextArea(
      this.editorRef.current, {
        autofocus: true,
        mode: 'gfm',
        lineWrapping: true,
        placeholder: 'Enter your markdown here ...',
        viewportMargin: Infinity
      });
    this.codemirror.on('change', this.onContentChange)
    this.setContent(this.props.bit);
    this.setDescription(this.props.bit);
  }

  setContent({content}) {
    this.codemirror.setValue(content || '');
  }

  setDescription({description}) {
    this.descriptionRef.current.innerText = description || '';
  }

  componentDidUpdate() {
    const bit = this.props.bit || {};
    if (bit.content !== this.codemirror.getValue()) {
      this.setContent(bit);
    }
    if (bit.description !== this.descriptionRef.current.innerText) {
      this.setDescription(bit);
    }
  }

  onContentChange(editor, changeObj) {
    if (changeObj.origin !== 'setValue') {
      this.props.onChange({content: editor.getValue()})
    }
  }

  onDescriptionChange(event) {
    this.props.onChange({description: event.target.innerText});
  }

  render() {
    return <section className="fl cf w-100 mt0 border-box">
      <h1 contentEditable="true" className="f3 f2-ns bg-washed-yellow pb3"
          onChange={this.onDescriptionChange}
          ref={this.descriptionRef} 
          placeholder="Enter a title ..."
          onInput={this.onDescriptionChange}
      />
      <article className="cf w-100 pt0">         
      <textarea 
        id="content" 
        className="CodeMirror"
        placeholder="Enter your markdown here ..."
        ref={this.editorRef}
      ></textarea>
      </article>
    </section>
  }
}

const Viewer = ({ bit, user }) => {
  const { year, monthDay } = getDateParts(bit.created_at);

  return <section className="fl cf w-100 mt0 border-box dark-gray">
    <h1 className="f3 cf fw6 f1-ns">{bit ? bit.description : ''}</h1>  
    <time className="f5 pa0 lighter-gray">{monthDay} {year}</time> 
    <article className="f4 w-100 pt3" dangerouslySetInnerHTML={{__html: MarkedWithHljs(bit && bit.content || '')}} />
  </section>
}

export default BitPage;
