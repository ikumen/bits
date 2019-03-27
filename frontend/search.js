import React from 'react';

class Search extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      show: false
    }
    this.hide = this.hide.bind(this);
  }

  open() {

  }

  hide() {
    this.setState({show: false})
  }

  render() {
    return <div className="tc">
      <i className="f3 f2-ns material-icons dim lighter-gray pointer" 
            onClick={()=> this.setState({show: true}) }
          >search
      </i>
      {!this.state.show && <SearchModal onHide={this.hide} />}
      </div>
  }
}
 
const SearchModal = ({onHide}) => {

  return <div className="modal bg-light-gray cf">
    <div className="block pa3 tr">
      <i className="material-icons md-36 gray dim top-0 right-0 pointer"
          onClick={()=> onHide()}
          title="Done">close</i>
    </div>
    <div className="fl w-100 pa2">
      <input type="text" className="input-reset f3 fw3 w-90 w-80-ns" placeholder="Search" />
    </div>  
    <section className="fl w-100 pa2">
      hello
    </section>
  </div>
}

export default Search;
