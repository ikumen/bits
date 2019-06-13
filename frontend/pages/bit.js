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
    this.state = {bit:{}, isDeleted: false}
    this.onChange = this.onChange.bind(this);
    this.save = this.save.bind(this);
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
        bit: {id: 'new', description: '', content: '', published_at: ''}, 
        status: ''
      });
    } else {
      BitService.get(id).then(bit => this.setState({
        bit: {
          id: bit.id,
          description: bit.description,
          content: bit.content,
          published_at: bit.published_at
        }
      }))
    }
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevProps.match.params.id !== this.props.match.params.id) {
      this.loadBit(this.props.match.params.id);
    }
  }

  onChange({description, content, publishedAt}) {
    const { bit } = this.state;
    if (description !== undefined) 
      bit.description = description;
    if (content !== undefined) 
      bit.content = content;
    if (publishedAt !== undefined) 
      bit.published_at = publishedAt;
    
    this.setState({ bit })
    if (this.autoSaveId) {
      clearTimeout(this.autoSaveId);
    }
    this.setState({status: 'Changes detected ...'}); 
    this.autoSaveId = setTimeout(this.onSave, 10000);
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
      this.save(this.state.bit, this.onSaveSuccess);
    }
  }

  save(bit, callback) {
    const successHandler = callback === undefined ?
      () => {} :
      (next) => callback(bit, next);

    bit.id === 'new' ?
      BitService.create(bit).then(successHandler):
      BitService.update(bit).then(successHandler);
  }

  componentWillUnmount() {
    const { bit, isDeleted } = this.state;
    if (this.autoSaveId) {
      clearTimeout(this.autoSaveId);
    }
    if (this.props.match.params.edit === 'edit' && !isDeleted) {
      /* force autosave if: hasn't been deleted, existing bit, or new bit with some edits */
      if (bit.id !== 'new' || (
          (bit.description || '').trim() !== '' ||
          (bit.content || '').trim() !== '')) {
        this.save(bit);
      }
    }
  }

  onDelete() {
    const {bit} = this.state;
    /* State changes are not immediate, so delete once we've
    cleaned up state and cleared bit. */
    this.setState({isDeleted: true}, () => {
      if (bit.id === 'new') {
        this.props.history.replace('/');
      } else {
        BitService.delete(bit.id)
          .then(()=> this.props.history.replace('/'));
      }
    });
  }

  render() {
    const isEdit = this.props.match.params.edit === 'edit';
    const { user={} } = this.props;
    const { bit, status } = this.state;
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
    replace={false}>Markdown</Link>
);

class Editor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isValidPublishedAt: true}
    this.descriptionRef = React.createRef();
    this.editorRef = React.createRef();
    this.publishedAtRef = React.createRef();
    this.onContentChange = this.onContentChange.bind(this);
    this.onDescriptionChange = this.onDescriptionChange.bind(this);
    this.onPublishedAtChange = this.onPublishedAtChange.bind(this);
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
    this.setPublishedAt(this.props.bit)
  }

  setContent({content}) {
    this.codemirror.setValue(content || '');
  }

  setDescription({description}) {
    this.descriptionRef.current.innerText = description || '';
  }

  setPublishedAt({published_at}) {
    this.publishedAtRef.current.innerText = published_at || '';
  }

  componentDidUpdate() {
    const bit = this.props.bit || {};
    if (bit.content !== this.codemirror.getValue())
      this.setContent(bit);
    if (bit.description !== this.descriptionRef.current.innerText)
      this.setDescription(bit);
    if (bit.published_at != this.publishedAtRef.current.innerText)
      this.setPublishedAt(bit);
  }

  onContentChange(editor, changeObj) {
    if (changeObj.origin !== 'setValue') {
      this.props.onChange({content: editor.getValue()})
    }
  }

  onDescriptionChange(event) {
    this.props.onChange({description: event.target.innerText});
  }

  onPublishedAtChange(event) {
    const dateString = event.target.innerText;
    // very naive date formatting check
    const re = /^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$/;
    const isValid = !isNaN(Date.parse(dateString)) && re.test(dateString);
    this.setState({'isValidPublishedAt': isValid})
    this.props.onChange({publishedAt: dateString});
  }

  render() {
    const { isValidPublishedAt } = this.state;
    return <section className="fl cf w-100 mt0 border-box">
      <h1 contentEditable="true" className="f3 f2-ns bg-washed-yellow"
          onChange={this.onDescriptionChange}
          ref={this.descriptionRef} 
          placeholder="Enter a title ..."
          onInput={this.onDescriptionChange}
      />
      <div contentEditable="true" className={`f5 cf w-25 pa0 bg-washed-yellow ba ${isValidPublishedAt ? 'b--washed-yellow' : 'b--red'}`}
        onChange={this.onPublishedAtChange}
        ref={this.publishedAtRef}
        placeholder="2019-01-01"
        onInput={this.onPublishedAtChange}>
      </div>
      <article className="cf w-100 pt4 f4">         
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
  const { year, monthDay } = getDateParts(bit.published_at);

  return <section className="fl cf w-100 mt0 border-box dark-gray">
    <h1 className="f3 cf fw6 f2-ns">{bit ? bit.description : ''}</h1>  
    <time className="f5 pa0 lighter-gray">{monthDay} {year}</time> 
    <article className="f4 w-100 pt3" dangerouslySetInnerHTML={{__html: MarkedWithHljs(bit && bit.content || '')}} />
  </section>
}

export default BitPage;
