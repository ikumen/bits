import React from 'react';

/** Generic wrapper for top level pages .*/
const Page = (props) => (
  // <main className="fl w-100 pa3 ph5-m ph6-ns border-box">
  <main className="fl w-100 pa3 ph5-m ph6-ns break-word border-box">
    {props.children}
  </main>
);

module.exports = {
  Page
}
