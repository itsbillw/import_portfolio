/* globals Chart:false, feather:false */

(function() {
  'use strict'

  feather.replace()

}())

toggle = function(source) {
  var checkboxes = document.querySelectorAll('input[type="checkbox"]');
  for (var i = 0; i < checkboxes.length; i++) {
    if (checkboxes[i] != source)
      checkboxes[i].checked = source.checked;
  }
}
