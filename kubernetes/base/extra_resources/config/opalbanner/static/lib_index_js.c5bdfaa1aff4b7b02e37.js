"use strict";
(self["webpackChunkopalbanner"] = self["webpackChunkopalbanner"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);

function generateContent() {
    return 'OPAL_BANNER_TEXT';
}
const plugin = {
    id: 'contentheader:plugin',
    autoStart: true,
    activate: (app) => {
        console.log('JupyterLab extension contentheader is activated!');
        const widget = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget();
        widget.addClass('banner-widget');
        widget.node.textContent = generateContent();
        const rootLayout = app.shell.layout;
        rootLayout.insertWidget(0, widget);
    },
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.c5bdfaa1aff4b7b02e37.js.map