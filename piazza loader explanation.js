jQuery
Bootstrap.js
jQuery plugin: FancyBox

PEM = new EventManager();

var P = {};
P.modules = {
  user: false,
  network: false,
  modules: {}, // this is a hashmap of all loaded modules
  cacheBuster: 0, // this should be initialized to current version for cache busting
  data: {}, // for managing data
  dataLoading: {},
  dataCallbacks: {},
  ...
  (functions here)
}

$(function() {
    if (P.modules.user)
        P.modules.initUser();
})

/* Piazza Template Manager */
var PTM = {
    ...
};

// various functions

Nginx Push Stream <pushstream.js>
theme.js
jQuery plugin: blockUI

PA = {
    ...
    user: {},
    userQueue: [],  // all users I don't know, but need to get
    ...
}

jQuery plugin: Tokenizing Autocomplete Text Entry
moment.js

<17414 lines>




PA.getUserName = function(id, ...) {
    PA.users[id] => actual name
}






window.onerror = (function() {
  var MAX_COUNT = 2;
  var API_URL = '/logic/api?method=generic.report_js_error&aid=' +
    (new Date()).getTime().toString(36) + Math.round(Math.random() * 1679616).toString(36);

  var reportError = function(params) {
    err_count++;
    if(err_count > MAX_COUNT) {
      return;
    }
    if (params.message && typeof(params.message) == 'string' && params.message.indexOf("Error connecting to extension") >= 0) return; // we don't want these
    params.location = window.location.toString();
    if(PA && PA.user && PA.user.id) {
      params.uid = PA.user.id;
    }
    $.ajax({
      url: API_URL,
      data: JSON.stringify({
        'method': 'generic.report_js_error', 
        'params': params
      }),
      type: 'POST',
      dataType: 'json'
    });
  };

  // catch uncaught JS exceptions (the actual window.onerror)
  return function(message, url, line) {
    reportError({
      type: 'js_exception',
      message: message,
      url: url,
      line: line
    });
  };
})();